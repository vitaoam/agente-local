import subprocess

PROTECTED_PROCESSES = {
    "csrss.exe", "svchost.exe", "winlogon.exe", "lsass.exe",
    "services.exe", "smss.exe", "wininit.exe", "dwm.exe",
    "system", "registry", "explorer.exe",
}

PROCESS_ALIASES = {
    "paint": "mspaint.exe",
    "bloco de notas": "notepad.exe",
    "notepad": "notepad.exe",
    "calculadora": "calculatorapp.exe",
    "explorer": "explorer.exe",
    "edge": "msedge.exe",
    "navegador": "msedge.exe",
    "chrome": "chrome.exe",
    "firefox": "firefox.exe",
    "terminal": "windowsterminal.exe",
    "powershell": "powershell.exe",
    "cmd": "cmd.exe",
    "ollama": "ollama.exe",
    "word": "winword.exe",
    "excel": "excel.exe",
    "vscode": "code.exe",
    "cursor": "cursor.exe",
}


def _resolve_process_name(nome: str) -> str:
    nome_lower = nome.strip().lower()
    if nome_lower in PROCESS_ALIASES:
        return PROCESS_ALIASES[nome_lower]
    if not nome_lower.endswith(".exe"):
        return nome_lower + ".exe"
    return nome_lower


def verificar_processo(nome: str) -> dict:
    if not nome or not nome.strip():
        return {"success": False, "message": "Nome do processo não informado.", "data": None}

    proc_name = _resolve_process_name(nome)

    try:
        result = subprocess.run(
            ["tasklist", "/FI", f"IMAGENAME eq {proc_name}"],
            capture_output=True,
            text=True,
            timeout=10,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        output = result.stdout.strip()

        if proc_name.lower() in output.lower():
            lines = [l for l in output.split("\n") if proc_name.lower() in l.lower()]
            count = len(lines)
            return {
                "success": True,
                "message": f"'{nome}' está em execução ({count} processo(s)).",
                "data": {"running": True, "count": count, "process": proc_name},
            }
        return {
            "success": True,
            "message": f"'{nome}' NÃO está em execução.",
            "data": {"running": False, "process": proc_name},
        }
    except Exception as e:
        return {"success": False, "message": f"Erro ao verificar: {e}", "data": None}


def listar_processos() -> dict:
    try:
        result = subprocess.run(
            ["tasklist", "/FO", "CSV", "/NH"],
            capture_output=True,
            text=True,
            timeout=10,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )

        procs: dict[str, int] = {}
        for line in result.stdout.strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            parts = line.split('","')
            if parts:
                name = parts[0].strip('"')
                if name.lower() not in PROTECTED_PROCESSES and name:
                    procs[name] = procs.get(name, 0) + 1

        sorted_procs = sorted(procs.items(), key=lambda x: x[1], reverse=True)[:25]
        lines = [f"  {name} ({count}x)" for name, count in sorted_procs]

        return {
            "success": True,
            "message": f"Processos em execução (top 25):\n" + "\n".join(lines),
            "data": {"processes": dict(sorted_procs)},
        }
    except Exception as e:
        return {"success": False, "message": f"Erro ao listar: {e}", "data": None}


def fechar_processo(nome: str) -> dict:
    if not nome or not nome.strip():
        return {"success": False, "message": "Nome do processo não informado.", "data": None}

    proc_name = _resolve_process_name(nome)

    if proc_name.lower() in PROTECTED_PROCESSES:
        return {
            "success": False,
            "message": f"'{proc_name}' é um processo protegido do sistema e não pode ser encerrado.",
            "data": None,
        }

    try:
        result = subprocess.run(
            ["taskkill", "/IM", proc_name, "/F"],
            capture_output=True,
            text=True,
            timeout=10,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )

        if result.returncode == 0:
            return {
                "success": True,
                "message": f"Processo '{nome}' encerrado com sucesso.",
                "data": {"process": proc_name},
            }
        stderr = result.stderr.strip()
        if "not found" in stderr.lower() or "não encontrad" in stderr.lower():
            return {"success": False, "message": f"Processo '{nome}' não encontrado.", "data": None}
        return {"success": False, "message": f"Não foi possível encerrar '{nome}': {stderr}", "data": None}
    except Exception as e:
        return {"success": False, "message": f"Erro ao encerrar: {e}", "data": None}
