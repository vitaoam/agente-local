import os
from pathlib import Path

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b")

USER_HOME = Path.home()
DESKTOP_PATH = USER_HOME / "Desktop"
DOCUMENTS_PATH = USER_HOME / "Documents"
DOWNLOADS_PATH = USER_HOME / "Downloads"

ALLOWED_PATHS: list[Path] = [DESKTOP_PATH, DOCUMENTS_PATH, DOWNLOADS_PATH]

SUBPROCESS_TIMEOUT = 10

TOOLS_REQUIRING_CONFIRMATION = {"criar_pasta_desktop", "mover_arquivo", "renomear_arquivo", "fechar_processo"}
