# MANULO  

**LLM 기반 전자제품 설명서 질의응답 시스템**  

사용자가 업로드한 전자제품 설명서를 벡터화하여 저장하고,  
자연어 질문에 대해 **AI가 실시간으로 응답**하는 챗봇 서비스입니다.  

단순 키워드 검색을 넘어 **문맥 기반 답변**을 제공하여,  
제품 이해도를 높이고 활용 경험을 풍부하게 만듭니다.  

## 주요 폴더 및 파일 구조

```

├── pyproject.toml      # 프로젝트 의존성 및 패키지 설정
├── README.md           # 프로젝트 문서
├── uv.lock             # uv 패키지 관리 Lock 파일
├── app/
│   ├── main.py         # FastAPI 진입점 (서버 실행)
│   ├── api/            # API 라우터 및 엔드포인트
│   ├── core/
│   │   └── llm\_client.py  # LLM 클라이언트 설정 (OpenAI 등)
│   ├── docs/
│   │   └── iphone.pdf  # 예시 문서 (RAG 학습 데이터)
│   └── rag/
│       ├── nodes.py    # LangGraph 노드 정의
│       ├── state.py    # 상태 관리 (RAG 상태 저장)
│       └── workflow\.py # 전체 워크플로우 정의

```

### 주요 구성 요소
- **app/main.py**: 애플리케이션 진입점
- **app/core/llm_client.py**: LLM 연동 클라이언트
- **app/rag/**: RAG 워크플로우, 상태 관리, 노드 정의
- **app/docs/**: 예시 PDF 문서

## 설치 및 실행 방법

1. 의존성 설치
   ```bash
  
   pip install uv
   uv pip install -r requirements.txt
   ```

2. 애플리케이션 실행
   ```bash
   uv run uvicorn app.main:app --reload
   ```

## 기능 예시
- PDF 등 문서에서 정보 추출
- LLM 기반 질의응답
- RAG 워크플로우 관리



## 📄 추가 문서  

- [프로젝트 소개 (Wiki)](../../wiki/01_프로젝트-소개)
- [기획 발표 자료 (PDF, Google Drive)](https://drive.google.com/file/d/1Z77Z9GfBNW_sZkw0HPKqHdN1baJ4IMEZ/view?usp=sharing)
- [중간 발표 자료 (PDF, Google Drive)](https://drive.google.com/file/d/16jz149EbOBO0RoWTA0t9kU1WicXP6L5J/view?usp=sharing)
