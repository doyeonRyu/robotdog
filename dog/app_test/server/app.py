# server/app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routes_gpt import router as gpt_router

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 단계: 데스크탑 브라우저 접근 허용
    allow_methods=["*"],
    allow_headers=["*"],
)

# TTS 파일을 내려줄 정적 경로 (예: /static/tts/xxx.mp3)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(gpt_router)
