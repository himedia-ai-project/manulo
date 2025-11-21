from typing import List, Tuple
import os, tempfile, requests
from app.core import llm_client
from app.rag.state import GraphState, QueryState

# 랭체인
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from app.rag.state import GraphState, QueryState
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

STORES_DIR = "./stores"
os.makedirs(STORES_DIR, exist_ok=True)
MAX_HISTORY = 10


# URL의 PDF를 임시파일로 저장하고 경로를 state['temp_path']에 기록
def fetch_pdf(state: GraphState) -> GraphState:
    url = state["file_path"]
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        temp_file.write(resp.content)
        state["temp_path"] = temp_file.name
    return state


# 임시파일을 읽어 state['documents']에 로드하고 항상 임시파일을 삭제
def load_pdf(state: GraphState) -> GraphState:
    temp_path = state.get("temp_path")
    try:
        state["documents"] = PyPDFLoader(temp_path).load()
        return state
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


# 문서 청크
def split_chunks(state: GraphState) -> GraphState:
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    state["chunks"] = splitter.split_documents(state.get("documents", []))
    return state


# 임베딩, 벡터스토어 생성(FAISS)
def create_vectorstore(state: GraphState) -> GraphState:
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    state["vectorstore"] = FAISS.from_documents(state.get("chunks", []), embeddings)
    return state


# FAISS 디스크 저장
def save_vectorstore(state: GraphState) -> GraphState:
    pdf_id = str(state.get("pdf_id"))
    if not pdf_id:
        raise ValueError("pdf_id가 state에 존재하지 않습니다.")

    faiss_store: FAISS | None = state.get("vectorstore")
    if faiss_store is None:
        raise ValueError("vectorstore가 state에 존재하지 않습니다.")

    path = os.path.join(STORES_DIR, pdf_id)
    os.makedirs(path, exist_ok=True)
    faiss_store.save_local(path)
    state["store_path"] = path

    return state


# 1.Vectorstore 로드
def load_vectorstore(state: QueryState) -> QueryState:
    pdf_id = str(state.get("pdf_id"))
    if not pdf_id:
        raise ValueError("pdf_id가 state에 없습니다.")

    path = os.path.join(STORES_DIR, pdf_id)
    if not os.path.exists(path):
        raise ValueError(f"PDF {pdf_id}에 해당하는 저장소가 존재하지 않습니다.")

    state["vectorstore"] = FAISS.load_local(
        path,
        OpenAIEmbeddings(model="text-embedding-3-small"),
        allow_dangerous_deserialization=True,
    )
    return state


# 2.질문에 대한 context 검색
def retrieve_context(state: QueryState) -> QueryState:
    vectorstore = state.get("vectorstore")
    if vectorstore is None:
        raise ValueError(
            "vectorstore가 state에 없습니다. load_vectorstore가 먼저 실행되어야 합니다."
        )
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    docs = retriever.get_relevant_documents(state["question"])
    state["context"] = "\n\n".join([doc.page_content for doc in docs])
    return state


# 3.답변 생성
async def generate_answer(state: QueryState) -> QueryState:
    system_prompt = """
      You are an assistant that answers questions based on the provided context.
    - Always use the information in the context.
    - Do not make up answers not present in the context.
    - If the question is outside the context, politely say you don't know.
    - Keep answers concise and clear.
    - Refer to previous conversation to maintain context."""

    # 이전 히스토리 가져오기
    messages: List[BaseMessage] = state.get("history", [])

    # 헬퍼 함수로 프롬프트 생성
    prompt_messages = [("system", system_prompt)] + await messages_to_prompt(messages)
    prompt = ChatPromptTemplate.from_messages(prompt_messages)

    # LLM 호출
    chain = prompt | llm_client.llm | StrOutputParser()
    answer = await chain.ainvoke({})

    # AI 답변 메시지로 추가
    messages.append(AIMessage(content=answer))

    # 상태 업데이트
    state["answer"] = answer
    state["history"] = messages
    return state


#  히스토리가 MAX_HISTORY 이상이면 요약하고 그렇지 않으면 그대로 반환하는 노드
async def summarize_history(state: QueryState) -> QueryState:
    messages: List[BaseMessage] = state.get("history", [])
    if len(messages) <= MAX_HISTORY:
        return state

    # BaseMessage → (role, content) 튜플 변환
    prompt_messages = await messages_to_prompt(messages)
    summary_text = "\n".join([content for role, content in prompt_messages])

    # 요약 프롬프트
    summary_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "Summarize the following conversation briefly:"),
            ("user", summary_text),
        ]
    )
    chain = summary_prompt | llm_client.llm | StrOutputParser()
    summary = await chain.ainvoke({})

    # 요약 결과만 남기고 히스토리 초기화
    state["history"] = [AIMessage(content=f"Conversation summary: {summary}")]
    return state


# 조건부 edge 함수 정의
def decide_next(state: QueryState):
    if len(state.get("history", [])) > MAX_HISTORY:
        return "summarize_history"
    return "generate_answer"


async def messages_to_prompt(messages: List[BaseMessage]) -> List[Tuple[str, str]]:
    """HumanMessage / AIMessage 리스트를 (role, content) 튜플로 변환"""
    prompt_messages = []
    for m in messages:
        if isinstance(m, HumanMessage):
            prompt_messages.append(("user", m.content))
        elif isinstance(m, AIMessage):
            prompt_messages.append(("assistant", m.content))
        else:
            raise ValueError(f"Unknown message type: {type(m)}")
    return prompt_messages
