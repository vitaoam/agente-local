import ctypes
import platform
import shutil
import socket
import string
from datetime import datetime


class _MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [
        ("dwLength", ctypes.c_ulong),
        ("dwMemoryLoad", ctypes.c_ulong),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]


def obter_ip() -> dict:
    hostname = socket.gethostname()
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(2)
        s.connect(("8.8.8.8", 80))
        ip_principal = s.getsockname()[0]
        s.close()
    except Exception:
        try:
            ip_principal = socket.gethostbyname(hostname)
        except Exception:
            ip_principal = "Não foi possível determinar"

    return {
        "success": True,
        "message": f"Hostname: {hostname}\nIP local: {ip_principal}",
        "data": {"hostname": hostname, "ip": ip_principal},
    }


def obter_hora_atual() -> dict:
    agora = datetime.now()

    dias_semana = {
        0: "segunda-feira",
        1: "terça-feira",
        2: "quarta-feira",
        3: "quinta-feira",
        4: "sexta-feira",
        5: "sábado",
        6: "domingo",
    }
    meses = {
        1: "janeiro",
        2: "fevereiro",
        3: "março",
        4: "abril",
        5: "maio",
        6: "junho",
        7: "julho",
        8: "agosto",
        9: "setembro",
        10: "outubro",
        11: "novembro",
        12: "dezembro",
    }

    dia_semana = dias_semana[agora.weekday()]
    mes = meses[agora.month]
    formatado = (
        f"{dia_semana}, {agora.day} de {mes} de {agora.year}, "
        f"{agora.strftime('%H:%M:%S')}"
    )

    return {
        "success": True,
        "message": formatado,
        "data": {"datetime": agora.isoformat(), "formatted": formatado},
    }


def info_sistema() -> dict:
    info = {
        "Sistema": f"{platform.system()} {platform.release()}",
        "Versão": platform.version(),
        "Hostname": platform.node(),
        "Processador": platform.processor(),
        "Arquitetura": platform.machine(),
    }

    try:
        mem = _MEMORYSTATUSEX()
        mem.dwLength = ctypes.sizeof(_MEMORYSTATUSEX)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(mem))
        total_gb = round(mem.ullTotalPhys / (1024**3), 1)
        avail_gb = round(mem.ullAvailPhys / (1024**3), 1)
        used_gb = round(total_gb - avail_gb, 1)
        info["RAM total"] = f"{total_gb} GB"
        info["RAM em uso"] = f"{used_gb} GB ({mem.dwMemoryLoad}%)"
        info["RAM livre"] = f"{avail_gb} GB"
    except Exception:
        pass

    lines = [f"  {k}: {v}" for k, v in info.items()]
    return {
        "success": True,
        "message": "Informações do sistema:\n" + "\n".join(lines),
        "data": info,
    }


def espaco_disco() -> dict:
    drives = []
    for letter in string.ascii_uppercase:
        drive = f"{letter}:\\"
        try:
            usage = shutil.disk_usage(drive)
            total_gb = round(usage.total / (1024**3), 1)
            used_gb = round(usage.used / (1024**3), 1)
            free_gb = round(usage.free / (1024**3), 1)
            pct = round(usage.used / usage.total * 100, 1)
            drives.append({
                "drive": f"{letter}:",
                "total": f"{total_gb} GB",
                "usado": f"{used_gb} GB",
                "livre": f"{free_gb} GB",
                "percentual": f"{pct}%",
            })
        except (OSError, FileNotFoundError):
            continue

    if not drives:
        return {"success": False, "message": "Não foi possível obter informações de disco.", "data": None}

    lines = [
        f"  {d['drive']}  {d['usado']} usados de {d['total']} ({d['percentual']}) — {d['livre']} livres"
        for d in drives
    ]
    return {
        "success": True,
        "message": "Espaço em disco:\n" + "\n".join(lines),
        "data": {"drives": drives},
    }
