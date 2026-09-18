from fastapi import APIRouter
import psutil
import time

router = APIRouter(prefix="/api/system", tags=["system"])
start_time = time.time()

@router.get("/")
def get_system_health():
    return {
        "status": "ONLINE",
        "uptime_seconds": int(time.time() - start_time),
        "cpu_usage_percent": psutil.cpu_percent(),
        "memory_usage_percent": psutil.virtual_memory().percent,
        "components": {
            "api": "ONLINE",
            "database": "CONNECTED",
            "ml_engine": "ONLINE",
            "zeek_adapter": "AVAILABLE",
            "scapy_adapter": "AVAILABLE"
        }
    }
