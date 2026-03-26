APP_ALIASES: dict[str, str] = {
    "paint": "mspaint",
    "bloco de notas": "notepad",
    "notepad": "notepad",
    "calculadora": "calc",
    "explorer": "explorer",
    "explorador": "explorer",
    "explorador de arquivos": "explorer",
    "edge": "msedge",
    "navegador": "msedge",
    "cmd": "cmd",
    "terminal": "wt",
    "powershell": "powershell",
    "configurações": "ms-settings:",
    "configuracoes": "ms-settings:",
}


def resolve_app(name: str) -> str | None:
    normalized = name.strip().lower()
    return APP_ALIASES.get(normalized)


def list_supported_apps() -> list[str]:
    return sorted(set(APP_ALIASES.keys()))
