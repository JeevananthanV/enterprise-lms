from fastapi import APIRouter

router = APIRouter()

@router.get("/status")
async def enrollment_domain_status():
    return {"domain": "enrollment", "status": "registered", "phase": "Phase 2+"}
