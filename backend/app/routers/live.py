from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.ingestion.live_capture import live_capture_service

router = APIRouter(prefix="/api/live", tags=["live"])

class StartRequest(BaseModel):
    interface: str

@router.get("/interfaces")
def get_interfaces():
    return {"interfaces": live_capture_service.get_interfaces()}

@router.post("/start")
def start_capture(req: StartRequest):
    if live_capture_service.is_running:
        raise HTTPException(status_code=400, detail="Capture already running")
    live_capture_service.start(req.interface)
    return {"message": "Capture started"}

@router.post("/stop")
def stop_capture():
    live_capture_service.stop()
    return {"message": "Capture stopped"}

@router.get("/status")
def get_status():
    return live_capture_service.stats
