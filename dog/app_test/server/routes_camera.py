# server/routes_camera.py
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import httpx

router = APIRouter()

@router.get("/camera")
async def camera_proxy():
    # 외부 MJPEG 스트림을 프록시 (필요 시 주소 수정)
    url = f"http://{ '127.0.0.1' }:{ 9000 }/?action=stream"
    client = httpx.AsyncClient(timeout=None)
    async def _iter():
        async with client.stream("GET", url) as r:
            async for chunk in r.aiter_bytes():
                yield chunk
    return StreamingResponse(_iter(), media_type="multipart/x-mixed-replace; boundary=--frame")
