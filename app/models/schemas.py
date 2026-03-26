from pydantic import BaseModel
from typing import Optional, Any


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    type: str
    message: str
    action_id: Optional[str] = None
    details: Optional[dict] = None


class PendingAction(BaseModel):
    action_id: str
    tool_name: str
    tool_args: dict
    description: str


class ConfirmationRequest(BaseModel):
    action_id: str


class BasicToolResult(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
