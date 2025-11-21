# manulo

> 전자제품 설명서 질의응답 챗봇

manulo는 사용자가 업로드한 전자제품 설명서를 벡터화해 저장하고,
AI 챗봇이 해당 설명서 내용을 기반으로 자연어 질문에 실시간으로 답변하는 서비스입니다.

---

## 기술 스택

- **Frontend:** JavaScript (React)
- **Backend:** Java(Spring Boot), Python(FastAPI+LangChain)
- **Storage:** AWS S3
- **Database:** PostgreSQL, Redis(세션 문맥 관리)
- **Vector DB:** FAISS
- **AI & Embedding:** OpenAI Embedding API

---

## 주요 기능

### 제품 사용 설명서 등록 (AI 임베딩 파이프라인)

- Java(Spring Boot): PDF S3 업로드 → URL을 Python(FastAPI)에 전달
- Python(FastAPI): PDF 다운로드 → 전처리 → 텍스트 청크 분리
- OpenAI Embedding으로 벡터화 → FAISS 벡터스토어 생성 및 저장

### 대화형 질의응답 (RAG 기반 챗봇)

- 사용자 질문 수신 후 Redis로 세션 문맥 관리
- FAISS 유사도 검색 + LangGraph 기반 LLM(OpenAI) 응답 생성
- 제품 설명서를 기반으로 실시간 대화형 질의응답 제공

---

## 레포 링크

- [Main Backend (Java)](https://github.com/HIMEDIA-AI-PROJECT/FINAL-PROJECT)
- [AI Pipeline (Python)](https://github.com/HIMEDIA-AI-PROJECT/FINAL-PROJECT_AI)
