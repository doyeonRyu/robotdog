# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 단계: 데스크탑에서 접근 허용
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 서빙: app_test 폴더(현재 디렉터리)를 루트로 사용
# 따라서 http://<IP>:8000/ 로 접속하면 index.html 이 열립니다.
app.mount("/", StaticFiles(directory=".", html=True), name="static")

# (선택) 헬스체크
@app.get("/api/health")
def health():
    return {"ok": True}

# python -m app.main 으로 실행될 때 uvicorn 기동
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
