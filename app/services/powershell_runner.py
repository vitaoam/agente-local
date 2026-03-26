import subprocess

from app.config import SUBPROCESS_TIMEOUT

BLOCKED_PATTERNS = [
    "invoke-expression",
    "iex ",
    "iex(",
    "remove-item",
    "del ",
    "rm ",
    "set-executionpolicy",
    "reg add",
    "reg delete",
    "regedit",
    "format-volume",
    "clear-disk",
    "uninstall",
    "remove-appxpackage",
    "set-itemproperty",
    "new-psdrive",
    "[system.environment]::setenvironmentvariable",
]


def is_command_blocked(command: str) -> bool:
    cmd_lower = command.lower().strip()
    return any(pattern in cmd_lower for pattern in BLOCKED_PATTERNS)


def run_powershell(command: str) -> dict:
    if is_command_blocked(command):
        return {
            "success": False,
            "stdout": "",
            "stderr": "Comando bloqueado por razões de segurança.",
        }
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", command],
            capture_output=True,
            text=True,
            timeout=SUBPROCESS_TIMEOUT,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "stdout": "",
            "stderr": "O comando excedeu o tempo limite de execução.",
        }
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Erro ao executar comando: {e}",
        }
