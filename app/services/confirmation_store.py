import uuid

from app.models.schemas import PendingAction


class ConfirmationStore:
    def __init__(self):
        self._pending: dict[str, PendingAction] = {}

    def create(self, tool_name: str, tool_args: dict, description: str) -> str:
        action_id = str(uuid.uuid4())[:8]
        self._pending[action_id] = PendingAction(
            action_id=action_id,
            tool_name=tool_name,
            tool_args=tool_args,
            description=description,
        )
        return action_id

    def get(self, action_id: str) -> PendingAction | None:
        return self._pending.get(action_id)

    def remove(self, action_id: str) -> bool:
        if action_id in self._pending:
            del self._pending[action_id]
            return True
        return False

    def clear(self):
        self._pending.clear()


confirmation_store = ConfirmationStore()
