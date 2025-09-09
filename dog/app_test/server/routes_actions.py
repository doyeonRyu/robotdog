# server/routes_actions.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import asyncio

# ① dog/__init__.py에 re-export 했다면 ↓
from dog import ActionDict
# ② re-export 안 했다면 아래 라인으로 바꿔도 됨
# from dog.actions_dictionary import ActionDict

class ActionRequest(BaseModel):
    '''
    목적: 웹으로부터 받은 동작명(action)을 검증해 서버로 전달
    입력값: action(str) - ActionDict의 키(예: 'stand','sit' 등)
    출력값: 없음(요청 바디 검증용)
    '''
    action: str

router = APIRouter()

@router.post("/api/action")
async def action_endpoint(req: ActionRequest):
    '''
    목적: 웹 버튼 클릭 → 로봇 동작 실행을 큐에 올리고 즉시 ACK 반환
    입력값: ActionRequest(JSON) - {"action":"stand"} 등
    출력값: dict - {"status":"ok","action":"stand"} 형태의 ACK
    '''
    action = req.action

    # 등록되지 않은 액션 처리
    if action not in ActionDict:
        raise HTTPException(status_code=400, detail=f"Unknown action: {action}")

    # 실제 동작은 쓰레드로 넘겨 이벤트루프 블로킹 방지
    fn = ActionDict[action]
    try:
        # 하드웨어 제어는 블로킹이 많으므로 to_thread로 분리
        asyncio.create_task(asyncio.to_thread(fn))
        return {"status": "ok", "action": action}
    except Exception as e:
        # 큐잉 자체가 실패한 경우만 서버 에러
        raise HTTPException(status_code=500, detail=f"queue failed: {e}")

@router.get("/api/actions")
async def list_actions():
    '''
    목적: 프론트가 현재 사용 가능한 액션 키 목록을 조회
    입력값: 없음
    출력값: dict - {"actions": [...]}  (ActionDict의 키 리스트)
    '''
    return {"actions": list(ActionDict.keys())}
