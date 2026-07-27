# 뉴스 & 트렌드 리포트 생성기

마케터와 기획자가 관심 키워드와 산업군을 입력하면, 최신 네이버 뉴스 최대 10건을 수집하고 OpenAI 기반 리포트로 핵심 이슈와 기획 시사점을 보여 주는 MVP 웹 서비스입니다.

## 현재 MVP 기능

- 키워드·산업군 입력과 빈 값 검증
- 네이버 뉴스 API 최신순 검색, 중복 URL 제거, 최대 10건 표시
- 기사 제목·요약·발행일·원문 링크 제공
- `gpt-5.4-nano` Structured Outputs 기반 전체 요약·핵심 이슈·근거 기사 ID·분석 한계 생성
- 뉴스 수집과 LLM 분석 실패 시 안전한 오류 메시지 표시

> 기획 문서에는 향후 DART·연합뉴스 RSS 기반 분석 흐름이 정의되어 있습니다. 현재 구현은 네이버 뉴스 검색 기반 MVP입니다.

## 기술 스택

- Frontend: React, Vite
- Backend: Python, FastAPI, Pydantic
- External APIs: NAVER API Hub News Search, OpenAI Responses API

## 프로젝트 구조

```text
backend/
  app/api/                 # HTTP API Router
  app/models/              # 요청·리포트 데이터 모델
  app/services/            # 뉴스 검색·LLM 리포트 생성
  tests/unit/              # 백엔드 단위 테스트
frontend/
  src/components/          # 입력 폼·결과 화면
  src/services/            # 백엔드 API 요청
docs/                      # 요구사항·기능 분해·MVP 계획
```

## 사전 준비

- Python 3.11 이상
- Node.js 20 이상
- 네이버 뉴스 검색 API 인증 정보
- OpenAI API 키와 `gpt-5.4-nano` 사용 권한

## 환경 변수 설정

백엔드 폴더에 `.env` 파일을 만들고 아래 형식으로 값을 설정합니다. 실제 키는 Git에 커밋하지 않습니다.

```env
NAVER_API_HUB_CLIENT_ID=your_client_id
NAVER_API_HUB_CLIENT_SECRET=your_client_secret
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-5.4-nano
```

## 실행 방법

터미널을 두 개 열어 백엔드와 프론트엔드를 각각 실행합니다.

### 1. 백엔드

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

백엔드는 `http://localhost:8000`에서 실행됩니다. 상태 확인은 다음 명령을 사용합니다.

```powershell
Invoke-WebRequest http://localhost:8000/health
```

### 2. 프론트엔드

```powershell
cd frontend
npm install
npm run dev
```

브라우저에서 Vite가 출력한 주소(기본값 `http://localhost:5173`)를 엽니다.

## API 사용 예시

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri http://localhost:8000/api/reports/generate `
  -ContentType 'application/json' `
  -Body '{"keyword":"투자","industry":"반도체"}'
```

주요 엔드포인트는 다음과 같습니다.

- `GET /health`: 백엔드 상태 확인
- `POST /api/reports/validate`: 입력값 검증
- `POST /api/reports/search`: 뉴스 검색
- `POST /api/reports/generate`: 뉴스 검색과 LLM 리포트 생성

## 테스트와 빌드

```powershell
# 백엔드 단위 테스트
cd backend
python -m unittest discover -s tests/unit -p "test_*.py" -v

# 프론트엔드 프로덕션 빌드 확인
cd frontend
npm run build
```

정상 결과는 백엔드 테스트 전체 통과와 프론트엔드 `dist/` 생성입니다. 외부 API 오류가 발생하면 백엔드 터미널 로그와 `.env`의 변수명·사용 권한을 확인하세요. 키 값 자체는 로그나 화면에 출력하지 마세요.

## 제한 사항과 다음 단계

- 현재 뉴스 데이터 소스는 네이버 뉴스 API이며, 분석 대상은 최신순 최대 10건입니다.
- LLM 결과는 기사 제목·요약을 바탕으로 한 참고 정보이므로 원문 링크로 근거를 확인해야 합니다.
- DART 경쟁사 선정, 연합뉴스 RSS 수집, 기간·주차별 분석은 기획 문서에 정의된 후속 MVP 확장 항목입니다.
