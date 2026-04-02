import shutil
from pathlib import Path

from app.config import DESKTOP_PATH
from app.services.path_guard import validate_path, is_path_allowed

HIDDEN_FILES = {"desktop.ini", "thumbs.db"}


def listar_desktop() -> dict:
    desktop = DESKTOP_PATH
    if not desktop.exists():
        return {
            "success": False,
            "message": "A pasta da Área de Trabalho não foi encontrada.",
            "data": None,
        }

    items = []
    for item in sorted(desktop.iterdir()):
        if item.name.lower() in HIDDEN_FILES:
            continue
        items.append({
            "nome": item.name,
            "tipo": "pasta" if item.is_dir() else "arquivo",
            "caminho": str(item),
        })

    if not items:
        return {"success": True, "message": "A Área de Trabalho está vazia.", "data": []}

    lines = []
    for item in items:
        icone = "📁" if item["tipo"] == "pasta" else "📄"
        lines.append(f"{icone} {item['nome']} ({item['tipo']})")

    return {
        "success": True,
        "message": f"Itens na Área de Trabalho ({len(items)}):\n" + "\n".join(lines),
        "data": items,
    }


def criar_arquivo(nome: str, diretorio: str = "") -> dict:
    if not nome or not nome.strip():
        return {"success": False, "message": "Nome do arquivo não pode ser vazio.", "data": None}

    nome = nome.strip()
    invalid_chars = '<>:"/\\|?*'
    if any(c in nome for c in invalid_chars):
        return {"success": False, "message": f"Nome '{nome}' contém caracteres inválidos.", "data": None}

    if diretorio:
        base = Path(diretorio)
        if not base.is_absolute():
            base = DESKTOP_PATH / diretorio
    else:
        base = DESKTOP_PATH

    target = base / nome
    allowed, resolved, error_msg = validate_path(target)
    if not allowed:
        return {"success": False, "message": error_msg, "data": None}

    if not base.exists():
        return {
            "success": False,
            "message": f"O diretório '{base.name}' não existe.",
            "data": None,
        }

    if target.exists():
        return {
            "success": False,
            "message": f"Já existe um item chamado '{nome}' neste local.",
            "data": None,
        }

    try:
        target.touch()
        return {
            "success": True,
            "message": f"Arquivo '{nome}' criado com sucesso em '{base}'.",
            "data": {"caminho": str(target)},
        }
    except Exception as e:
        return {"success": False, "message": f"Erro ao criar arquivo: {e}", "data": None}


def criar_pasta_desktop(nome: str) -> dict:
    if not nome or not nome.strip():
        return {"success": False, "message": "Nome da pasta não pode ser vazio.", "data": None}

    nome = nome.strip()
    invalid_chars = '<>:"/\\|?*'
    if any(c in nome for c in invalid_chars):
        return {
            "success": False,
            "message": f"Nome '{nome}' contém caracteres inválidos.",
            "data": None,
        }

    target = DESKTOP_PATH / nome
    allowed, resolved, error_msg = validate_path(target)
    if not allowed:
        return {"success": False, "message": error_msg, "data": None}

    if target.exists():
        return {
            "success": False,
            "message": f"Já existe um item chamado '{nome}' na Área de Trabalho.",
            "data": None,
        }

    try:
        target.mkdir(parents=False, exist_ok=False)
        return {
            "success": True,
            "message": f"Pasta '{nome}' criada com sucesso na Área de Trabalho.",
            "data": {"caminho": str(target)},
        }
    except Exception as e:
        return {"success": False, "message": f"Erro ao criar pasta: {e}", "data": None}


def mover_arquivo(origem: str, destino: str) -> dict:
    allowed_orig, resolved_orig, err_orig = validate_path(origem)
    if not allowed_orig:
        return {"success": False, "message": err_orig, "data": None}

    allowed_dest, resolved_dest, err_dest = validate_path(destino)
    if not allowed_dest:
        return {"success": False, "message": err_dest, "data": None}

    if not resolved_orig.exists():
        return {
            "success": False,
            "message": f"O arquivo '{resolved_orig.name}' não foi encontrado.",
            "data": None,
        }

    if resolved_dest.is_dir():
        resolved_dest = resolved_dest / resolved_orig.name

    if resolved_dest.exists():
        return {
            "success": False,
            "message": f"Já existe um arquivo em '{resolved_dest}'.",
            "data": None,
        }

    try:
        shutil.move(str(resolved_orig), str(resolved_dest))
        return {
            "success": True,
            "message": f"Arquivo '{resolved_orig.name}' movido com sucesso para '{resolved_dest.parent.name}'.",
            "data": {"origem": str(resolved_orig), "destino": str(resolved_dest)},
        }
    except Exception as e:
        return {"success": False, "message": f"Erro ao mover arquivo: {e}", "data": None}


def renomear_arquivo(caminho: str, novo_nome: str) -> dict:
    allowed, resolved, error_msg = validate_path(caminho)
    if not allowed:
        return {"success": False, "message": error_msg, "data": None}

    if not resolved.exists():
        return {
            "success": False,
            "message": f"O arquivo '{resolved.name}' não foi encontrado.",
            "data": None,
        }

    novo_nome = novo_nome.strip()
    invalid_chars = '<>:"/\\|?*'
    if any(c in novo_nome for c in invalid_chars):
        return {
            "success": False,
            "message": f"Nome '{novo_nome}' contém caracteres inválidos.",
            "data": None,
        }

    new_path = resolved.parent / novo_nome
    allowed_new, _, err_new = validate_path(new_path)
    if not allowed_new:
        return {"success": False, "message": err_new, "data": None}

    if new_path.exists():
        return {
            "success": False,
            "message": f"Já existe um item chamado '{novo_nome}' neste local.",
            "data": None,
        }

    try:
        resolved.rename(new_path)
        return {
            "success": True,
            "message": f"Arquivo renomeado de '{resolved.name}' para '{novo_nome}'.",
            "data": {"caminho_anterior": str(resolved), "novo_caminho": str(new_path)},
        }
    except Exception as e:
        return {"success": False, "message": f"Erro ao renomear: {e}", "data": None}
