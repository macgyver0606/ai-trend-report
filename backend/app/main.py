from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.api.reports import router as reports_router


load_dotenv()


app = FastAPI(title="뉴스 & 트렌드 리포트 생성기 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(reports_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
