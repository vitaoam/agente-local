import re
import subprocess


def ping_host(host: str) -> dict:
    if not host or not host.strip():
        return {"success": False, "message": "Host não informado.", "data": None}

    host = host.strip()
    if not re.match(r"^[a-zA-Z0-9._-]+$", host):
        return {"success": False, "message": "Nome de host inválido.", "data": None}

    try:
        result = subprocess.run(
            ["ping", "-n", "4", host],
            capture_output=True,
            text=True,
            timeout=15,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        output = result.stdout.strip()
        if result.returncode == 0:
            return {
                "success": True,
                "message": f"Ping para {host}:\n\n{output}",
                "data": {"host": host},
            }
        return {
            "success": False,
            "message": f"Falha no ping para {host}:\n\n{output}",
            "data": None,
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "message": f"Timeout ao pingar {host}.",
            "data": None,
        }
    except Exception as e:
        return {"success": False, "message": f"Erro ao pingar: {e}", "data": None}


def info_rede() -> dict:
    try:
        result = subprocess.run(
            ["ipconfig"],
            capture_output=True,
            text=True,
            timeout=10,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        output = result.stdout.strip()
        if not output:
            return {
                "success": False,
                "message": "Não foi possível obter informações de rede.",
                "data": None,
            }
        return {
            "success": True,
            "message": f"Informações de rede:\n\n{output}",
            "data": {"raw": output},
        }
    except Exception as e:
        return {"success": False, "message": f"Erro: {e}", "data": None}
