# app/main.py
# FastAPI 앱: 정적 웹(web/) 서빙 + 카메라 프록시(/camera) + API 라우트 + 조이스틱 WS
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse, JSONResponse
import asyncio
import httpx
import os

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 단계
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────────────────────
# 1) 정적 웹 서빙: web/ 폴더를 루트("/")로
#    http://PI:8000/  → app_test/web/index.html
# ─────────────────────────────────────────────────────────────
STATIC_DIR = os.path.join(os.path.dirname(__file__), "..", "web")
STATIC_DIR = os.path.abspath(STATIC_DIR)
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

# ─────────────────────────────────────────────────────────────
# 2) 카메라 프록시: :9000의 MJPEG 스트림을 :8000/camera 로 전달
#    (mjpg_streamer 등에서 보통 /?action=stream 경로 사용)
# ─────────────────────────────────────────────────────────────
CAMERA_SRC = os.environ.get("CAMERA_SRC", "http://127.0.0.1:9000/?action=stream")

@app.get("/camera")
async def camera_proxy():
    async def streamer():
        # 9000 쪽이 끊기면 재연결(간단 재시도) 루프
        while True:
            try:
                async with httpx.AsyncClient(timeout=None) as client:
                    async with client.stream("GET", CAMERA_SRC) as r:
                        async for chunk in r.aiter_bytes():
                            yield chunk
            except Exception:
                # 잠깐 쉬고 재시도
                await asyncio.sleep(1.0)
                continue
    # boundary는 대개 아래와 호환됩니다. 필요 시 실제 Content-Type에 맞춰 조정
    return StreamingResponse(
        streamer(),
        media_type="multipart/x-mixed-replace; boundary=--boundarydonotcross",
    )

# ─────────────────────────────────────────────────────────────
# 3) API 라우트: 이미 별도 라우터가 있다면 include_router로 연결
#    없으면 최소 더미 엔드포인트를 제공하여 프런트 테스트 가능
# ─────────────────────────────────────────────────────────────
# 예) 외부 라우터 사용
# from server.routes_gpt import router as gpt_router
# from server.routes_actions import router as actions_router
# app.include_router(gpt_router)
# app.include_router(actions_router)

# 더미(/api/chat, /api/chat-voice, /api/action) — 라우터가 아직 없을 때 임시 사용
@app.post("/api/chat")
async def api_chat(body: dict):
    text = (body or {}).get("text", "")
    # 실제 구현에서는 OpenAiHelper.dialogue(text) 호출 + TTS 파일 생성 후 URL 반환
    return {"reply": f"[echo] {text}", "audio_url": None}

@app.post("/api/chat-voice")
async def api_chat_voice():
    # 실제 구현에서는 업로드된 파일(FormData의 file)을 Whisper로 STT → GPT → TTS
    return {"text": "(voice stub)", "reply": "[echo] voice", "audio_url": None}

@app.post("/api/action")
async def api_action(body: dict):
    action = (body or {}).get("action", "")
    # 실제 구현에서는 robot/action_dictionary.py 매핑 실행
    return {"status": "ok", "action": action}

# ─────────────────────────────────────────────────────────────
# 4) 조이스틱 WebSocket: /ws/control
#    프런트에서 50ms 주기로 {vx,vy,wz} 전송 → 여기서 로봇 드라이버에 전달
# ─────────────────────────────────────────────────────────────
@app.websocket("/ws/control")
async def ws_control(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            data = await ws.receive_text()
            # TODO: robot/driver.py 의 send_velocity 로 연결
            # 예: driver.send_velocity(json.loads(data))
            # 지금은 에코만
            await ws.send_text(data)
    except Exception:
        await ws.close()

# ─────────────────────────────────────────────────────────────
# 5) 헬스체크
# ─────────────────────────────────────────────────────────────
@app.get("/api/health")
def health():
    return {"ok": True}

# ─────────────────────────────────────────────────────────────
# 로컬 실행 (python -m app.main)
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
