# server/routes_actions.py
from fastapi import APIRouter
from pydantic import BaseModel
from dog import ActionDict

router = APIRouter()

class ActionRequest(BaseModel):
    action: str

@router.post("/api/action")
async def action_endpoint(req: ActionRequest):
    action = req.action

    if action not in ActionDict:
        return {"status": "error", "detail": f"Unknown action: {action}"}

    try:
        # 매핑된 함수 실행
        ActionDict[action]()
        return {"status": "ok", "action": action}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
