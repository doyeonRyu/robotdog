from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 단계
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적(프런트) 서빙: http://<IP>:8000/ 에서 index.html 열림
app.mount("/", StaticFiles(directory=".", html=True), name="static")

# --- API 라우터 붙이기 ---
# 서버 라우터(있으면) 경로에 맞게 import 수정하세요.
# 예: robotdog/server/routes_gpt.py 라면 PYTHONPATH에 repo 루트를 넣고 아래처럼:
# from server.routes_gpt import router as gpt_router
# from server.routes_actions import router as actions_router
# app.include_router(gpt_router)
# app.include_router(actions_router)

# 임시 헬스체크
@app.get("/api/health")
def health():
    return {"ok": True}
