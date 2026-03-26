from fastapi import APIRouter

from app.models.schemas import ChatRequest, ChatResponse, ConfirmationRequest
from app.services.agent import process_message, confirm_action, cancel_action

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    result = await process_message(request.message)
    return ChatResponse(
        type=result.get("type", "response"),
        message=result.get("message", ""),
        action_id=result.get("action_id"),
    )


@router.post("/confirm", response_model=ChatResponse)
async def confirm(request: ConfirmationRequest):
    result = await confirm_action(request.action_id)
    return ChatResponse(
        type=result.get("type", "response"),
        message=result.get("message", ""),
    )


@router.post("/cancel", response_model=ChatResponse)
async def cancel(request: ConfirmationRequest):
    result = await cancel_action(request.action_id)
    return ChatResponse(
        type=result.get("type", "response"),
        message=result.get("message", ""),
    )
