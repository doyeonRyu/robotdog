# server/routes_actions.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from dog import ActionDict
from dog import Mydog  # Mydog 제어 클래스

router = APIRouter()
mydog = Mydog()
actions = ActionDict()

class ActionRequest(BaseModel):
    action: str

@router.post("/api/action")
async def action_endpoint(req: ActionRequest):
    action = req.action
    try:
        _ = actions[action]          # 동작 정의는 property에서 가져옴 (검증 용도)
        mydog.do_action(action)      # 여기서 실제 실행
        return {"status": "ok", "action": action}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Unknown or failed: {action} ({e})")
