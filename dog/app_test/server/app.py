# server/app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from routes_gpt import router as gpt_router
from routes_actions import router as actions_router   # ← 추가

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # 개발 단계: 전체 허용
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 (필요 시 web 또는 static 연결)
# web/index.html을 바로 서비스하고 싶다면:
app.mount("/", StaticFiles(directory="web", html=True), name="web")
# 기존 TTS 등 별도 정적이 있다면 유지
# app.mount("/static", StaticFiles(directory="static"), name="static")

# 라우터 등록
app.include_router(gpt_router)
app.include_router(actions_router)  # ← 추가
