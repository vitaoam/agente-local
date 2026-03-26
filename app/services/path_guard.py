from pathlib import Path

from app.config import ALLOWED_PATHS


def resolve_path(raw_path: str) -> Path:
    return Path(raw_path).expanduser().resolve()


def is_path_allowed(target: str | Path) -> bool:
    if isinstance(target, str):
        target = Path(target)
    resolved = target.resolve()
    for allowed in ALLOWED_PATHS:
        allowed_resolved = allowed.resolve()
        try:
            resolved.relative_to(allowed_resolved)
            return True
        except ValueError:
            continue
    return False


def validate_path(target: str | Path) -> tuple[bool, Path, str]:
    if isinstance(target, str):
        target = Path(target)
    resolved = target.resolve()
    if not is_path_allowed(resolved):
        return (
            False,
            resolved,
            f"Acesso negado: o caminho '{resolved}' está fora das pastas permitidas.",
        )
    return True, resolved, ""
