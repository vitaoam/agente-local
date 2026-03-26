import os
import subprocess

from app.services.app_registry import resolve_app, list_supported_apps


def abrir_app(nome_app: str) -> dict:
    if not nome_app or not nome_app.strip():
        return {
            "success": False,
            "message": "Nome do aplicativo não pode ser vazio.",
            "data": None,
        }

    executable = resolve_app(nome_app)
    if not executable:
        apps = ", ".join(list_supported_apps())
        return {
            "success": False,
            "message": (
                f"O aplicativo '{nome_app}' não é suportado ainda.\n"
                f"Aplicativos disponíveis: {apps}"
            ),
            "data": None,
        }

    try:
        if executable.startswith("ms-"):
            os.startfile(executable)
        else:
            subprocess.Popen(
                executable,
                creationflags=getattr(subprocess, "DETACHED_PROCESS", 0),
            )
        return {
            "success": True,
            "message": f"Aplicativo '{nome_app}' aberto com sucesso.",
            "data": {"app": nome_app, "executable": executable},
        }
    except FileNotFoundError:
        return {
            "success": False,
            "message": f"O executável para '{nome_app}' não foi encontrado no sistema.",
            "data": None,
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Erro ao abrir '{nome_app}': {e}",
            "data": None,
        }
