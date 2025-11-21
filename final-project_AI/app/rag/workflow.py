from langgraph.graph import StateGraph
from app.rag.nodes import (
    create_vectorstore,
    decide_next,
    generate_answer,
    fetch_pdf,
    load_pdf,
    load_vectorstore,
    retrieve_context,
    save_vectorstore,
    split_chunks,
    summarize_history,
)
from app.rag.state import GraphState, QueryState


# PDF Workflow
pdf_workflow = StateGraph(GraphState)
pdf_workflow.add_node("fetch_pdf", fetch_pdf)
pdf_workflow.add_node("load_pdf", load_pdf)
pdf_workflow.add_node("split_chunks", split_chunks)
pdf_workflow.add_node("create_vectorstore", create_vectorstore)
pdf_workflow.add_node("save_vectorstore", save_vectorstore)

pdf_workflow.set_entry_point("fetch_pdf")
pdf_workflow.add_edge("fetch_pdf", "load_pdf")
pdf_workflow.add_edge("load_pdf", "split_chunks")
pdf_workflow.add_edge("split_chunks", "create_vectorstore")
pdf_workflow.add_edge("create_vectorstore", "save_vectorstore")
pdf_workflow.set_finish_point("save_vectorstore")

pdf_graph = pdf_workflow.compile()

# Query Workflow
query_workflow = StateGraph(QueryState)
query_workflow.add_node("load_vectorstore", load_vectorstore)
query_workflow.add_node("retrieve_context", retrieve_context)
query_workflow.add_node("summarize_history", summarize_history)
query_workflow.add_node("generate_answer", generate_answer)
query_workflow.add_node("decide_next", decide_next)

query_workflow.set_entry_point("load_vectorstore")
query_workflow.add_edge("load_vectorstore", "retrieve_context")

# conditional edge 추가
query_workflow.add_conditional_edges("retrieve_context", decide_next)

query_workflow.add_edge("summarize_history", "generate_answer")
query_workflow.set_finish_point("generate_answer")

query_graph = query_workflow.compile()
