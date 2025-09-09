# server/app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from routes_gpt import router as gpt_router
from routes_actions import router as actions_router
from routes_control import router as control_router
from routes_camera import router as camera_router

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # 개발 단계: 전체 허용
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/", StaticFiles(directory="web", html=True), name="web")

app.include_router(gpt_router)
app.include_router(actions_router)
app.include_router(control_router)
app.include_router(camera_router)
