from fastapi import APIRouter

from app.services.ollama_client import ollama_client

router = APIRouter()


@router.get("/health")
async def health():
    ollama_status = await ollama_client.check_health()
    return {
        "status": "online",
        "agente": "Agente Local Windows 11",
        "versao": "1.0.0",
        "ollama": ollama_status,
    }
