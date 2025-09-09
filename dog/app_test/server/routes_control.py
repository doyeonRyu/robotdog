# server/routes_control.py
from fastapi import APIRouter, WebSocket
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

@router.websocket("/ws/control")
async def ws_control(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            msg = await ws.receive_json()
            # msg: {"type":"twist", "vx":.., "vy":.., "wz":..}
            # 여기서 로봇 실시간 제어 호출
            # robot.drive(vx=..., vy=..., wz=...)
            # 필요시 await ws.send_json({"ok": True})
    except Exception:
        pass  # 연결 종료 시 무시

class JoyReq(BaseModel):
    vx: float
    vy: float
    wz: float

@router.post("/api/joystick")
async def joystick_fallback(req: JoyReq):
    # WS가 없을 때 REST로 들어오는 케이스
    # robot.drive(vx=req.vx, vy=req.vy, wz=req.wz)
    return {"ok": True}
