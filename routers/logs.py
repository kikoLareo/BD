from fastapi import APIRouter, Request
from logging_config import logger
# Crea un router de FastAPI para manejar logs entrantes
router = APIRouter()

@router.post("/logs")
async def receive_log(request: Request):
    log_entry = await request.json()
    level = log_entry.get("level", "info").upper()
    message = log_entry.get("message", "No message provided")
    component = log_entry.get("component", "external")
    meta = log_entry.get("meta", {})

    # Registra el log en el nivel apropiado con el componente y metadatos
    log_method = getattr(logger, level.lower(), logger.info)
    log_method(f"[{component}] {message} | Meta: {meta}")
    return {"status": "Log received successfully"}