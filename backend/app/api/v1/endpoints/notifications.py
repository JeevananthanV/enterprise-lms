from fastapi import APIRouter

router = APIRouter()

@router.get("/status")
async def notifications_domain_status():
    return {"domain": "notifications", "status": "registered", "phase": "Phase 2+"}
