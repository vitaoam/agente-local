import re

from app.services.app_registry import resolve_app

PATTERNS: list[tuple[re.Pattern, str, callable]] = []


def _register(pattern: str, tool_name: str, extract_args):
    PATTERNS.append((re.compile(pattern, re.IGNORECASE), tool_name, extract_args))


def _no_args(_match) -> dict:
    return {}


# ---------------------------------------------------------------------------
# IP
# ---------------------------------------------------------------------------
_register(r"\bip\b", "obter_ip", _no_args)
_register(r"\bendere[cç]o\b.*\brede\b", "obter_ip", _no_args)

# ---------------------------------------------------------------------------
# Hora / Data
# ---------------------------------------------------------------------------
_register(r"\bhoras?\b", "obter_hora_atual", _no_args)
_register(r"\bque\s+dia\b", "obter_hora_atual", _no_args)
_register(r"\bhoje\b", "obter_hora_atual", _no_args)
_register(r"\bdata\b.*\batual\b", "obter_hora_atual", _no_args)

# ---------------------------------------------------------------------------
# Criar arquivo (DEVE vir antes de Listar Desktop)
# ---------------------------------------------------------------------------
def _extract_criar_arquivo(match) -> dict:
    text = match.string.strip()

    nome_m = re.search(
        r"(?:chamad[ao]|com\s+(?:o\s+)?nome)\s+['\"]?([a-zA-Z0-9\u00C0-\u024F_.\-]+)",
        text, re.IGNORECASE,
    )
    if not nome_m:
        nome_m = re.search(
            r"arquivo\s+(?:de\s+texto\s+)?(?:\.txt\s+)?(?:chamad[ao]\s+)?['\"]?([a-zA-Z0-9\u00C0-\u024F_.\-]+)",
            text, re.IGNORECASE,
        )
    if not nome_m:
        return None

    nome = nome_m.group(1).strip().strip("'\"")
    stopwords = {"no", "na", "do", "da", "dentro", "em", "desktop", "um", "uma", "de", "chamado", "chamada"}
    if nome.lower() in stopwords:
        return None

    if "." not in nome:
        nome += ".txt"

    result = {"nome": nome}

    dir_m = re.search(
        r"(?:dentro\s+d[ao]|n[ao])\s+pasta\s+['\"]?([a-zA-Z0-9\u00C0-\u024F_ -]+?)(?:['\"]?\s*(?:d[ao]\s+|$))",
        text, re.IGNORECASE,
    )
    if dir_m:
        dir_name = dir_m.group(1).strip()
        if dir_name.lower() not in {"área", "area", "trabalho", "desktop"}:
            result["diretorio"] = dir_name

    return result

_register(r"\bcri(?:ar|e|a)\b[^.]*\barquivo\b", "criar_arquivo", _extract_criar_arquivo)

# ---------------------------------------------------------------------------
# Criar pasta (DEVE vir antes de Listar Desktop)
# ---------------------------------------------------------------------------
def _extract_criar_pasta(match) -> dict:
    nome = match.group("nome").strip().strip("'\"")
    if nome:
        return {"nome": nome}
    return None

_register(
    r"\bcri(?:ar|e|a)\b.*\bpasta\b.*(?:chamad[ao]|nome|com o nome)\s+['\"]?(?P<nome>[a-zA-Z0-9\u00C0-\u024F_ -]+?)['\"]?\s*(?:no|na|$)",
    "criar_pasta_desktop",
    _extract_criar_pasta,
)
_register(
    r"\bcri(?:ar|e|a)\b.*\bpasta\b\s+['\"]?(?P<nome>[a-zA-Z0-9\u00C0-\u024F_ -]+?)['\"]?\s*$",
    "criar_pasta_desktop",
    _extract_criar_pasta,
)

# ---------------------------------------------------------------------------
# Listar Desktop
# ---------------------------------------------------------------------------
_register(r"\blist(?:ar|e|a)\b.*\b(?:desktop|[aá]rea|trabalho)\b", "listar_desktop", _no_args)
_register(r"\barquivos?\b.*\b(?:desktop|[aá]rea|trabalho)\b", "listar_desktop", _no_args)
_register(r"\b(?:o\s+que|quais)\b.*\b(?:desktop|[aá]rea|trabalho)\b", "listar_desktop", _no_args)
_register(r"\b(?:desktop|[aá]rea de trabalho)\b.*\barquivos?\b", "listar_desktop", _no_args)
_register(r"\bmostr(?:ar|e|a)\b.*\b(?:desktop|[aá]rea|trabalho)\b", "listar_desktop", _no_args)

# ---------------------------------------------------------------------------
# Abrir app
# ---------------------------------------------------------------------------
def _extract_app(match) -> dict:
    nome = match.group("app").strip().strip("'\"")
    if resolve_app(nome):
        return {"nome_app": nome}
    return None

_register(
    r"\babr(?:ir|a|e)\b\s+(?:o\s+|a\s+)?['\"]?(?P<app>[a-zA-Z0-9\u00C0-\u024F ]+?)['\"]?\s*$",
    "abrir_app",
    _extract_app,
)

# ---------------------------------------------------------------------------
# Ping
# ---------------------------------------------------------------------------
def _extract_host(match) -> dict:
    host = match.group("host").strip()
    if host:
        return {"host": host}
    return None

_register(
    r"\bping(?:a|ar|ue|ou)?\b[\s:]+(?:(?:a|o|na|no|em|para)\s+)?(?:m[aá]quina\s+)?(?P<host>[a-zA-Z0-9._-]+)",
    "ping_host",
    _extract_host,
)
_register(
    r"\bping\s+(?P<host>[a-zA-Z0-9._-]+)",
    "ping_host",
    _extract_host,
)

# ---------------------------------------------------------------------------
# Verificar processo
# ---------------------------------------------------------------------------
def _extract_proc(match) -> dict:
    nome = match.group("proc").strip().strip("'\"")
    if nome and len(nome) > 1:
        return {"nome": nome}
    return None

_register(
    r"(?:o\s+|a\s+)?(?P<proc>[a-zA-Z0-9_.]+)\s+(?:est[aá]|ta|t[aá])\s+(?:rodando|executando|aberto|ativo|funcionando|em\s+execu[cç][aã]o)",
    "verificar_processo",
    _extract_proc,
)
_register(
    r"(?:verifi(?:car|que)|checar?)\s+(?:se\s+)?(?:o\s+|a\s+)?(?P<proc>[a-zA-Z0-9_.]+)\b",
    "verificar_processo",
    _extract_proc,
)
_register(
    r"(?:est[aá]|ta|t[aá])\s+(?:rodando|executando|aberto)\s+(?:o\s+|a\s+)?(?P<proc>[a-zA-Z0-9_.]+)",
    "verificar_processo",
    _extract_proc,
)

# ---------------------------------------------------------------------------
# Fechar processo
# ---------------------------------------------------------------------------
def _extract_fechar(match) -> dict:
    nome = match.group("proc").strip().strip("'\"")
    if nome and len(nome) > 1:
        return {"nome": nome}
    return None

_register(
    r"\bfech(?:ar|e|a)\b\s+(?:o\s+|a\s+)?(?:processo\s+|app\s+|aplicativo\s+)?(?P<proc>[a-zA-Z0-9\u00C0-\u024F_ .]+?)\s*$",
    "fechar_processo",
    _extract_fechar,
)
_register(
    r"\bencerr(?:ar|e)\b\s+(?:o\s+|a\s+)?(?:processo\s+)?(?P<proc>[a-zA-Z0-9\u00C0-\u024F_ .]+?)\s*$",
    "fechar_processo",
    _extract_fechar,
)
_register(
    r"\bmat(?:ar|e)\b\s+(?:o\s+)?(?:processo\s+)?(?P<proc>[a-zA-Z0-9\u00C0-\u024F_ .]+?)\s*$",
    "fechar_processo",
    _extract_fechar,
)
_register(
    r"\bkill\b\s+(?P<proc>[a-zA-Z0-9._]+)",
    "fechar_processo",
    _extract_fechar,
)

# ---------------------------------------------------------------------------
# Listar processos
# ---------------------------------------------------------------------------
_register(r"\bprocess(?:os)?\b.*\b(?:rodando|execu[cç][aã]o|ativos?|abertos?)\b", "listar_processos", _no_args)
_register(r"\blist(?:ar|e|a)\b.*\bprocess(?:os)?\b", "listar_processos", _no_args)
_register(r"\bo\s+que\b.*\b(?:rodando|executando|aberto)\b", "listar_processos", _no_args)
_register(r"\btasklist\b", "listar_processos", _no_args)
_register(r"\bquais\b.*\bprocess(?:os)?\b", "listar_processos", _no_args)

# ---------------------------------------------------------------------------
# Info sistema
# ---------------------------------------------------------------------------
_register(r"\binfo(?:rma[çc][õo]es?)?\b.*\b(?:sistema|computador|pc|m[aá]quina)\b", "info_sistema", _no_args)
_register(r"\b(?:sistema|computador|pc|m[aá]quina)\b.*\binfo(?:rma[çc][õo]es?)?\b", "info_sistema", _no_args)
_register(r"\bdados?\b.*\b(?:sistema|computador|pc)\b", "info_sistema", _no_args)
_register(r"\b(?:qual|quanta?)\b.*\b(?:ram|mem[oó]ria)\b", "info_sistema", _no_args)
_register(r"\bprocessador\b", "info_sistema", _no_args)
_register(r"\bhostname\b", "info_sistema", _no_args)

# ---------------------------------------------------------------------------
# Espaço em disco
# ---------------------------------------------------------------------------
_register(r"\bespa[çc]o\b.*\bdisco\b", "espaco_disco", _no_args)
_register(r"\bdisco\b.*\bespa[çc]o\b", "espaco_disco", _no_args)
_register(r"\barmazenamento\b", "espaco_disco", _no_args)
_register(r"\bdisco\b.*\b(?:cheio|livre|usado|lotado)\b", "espaco_disco", _no_args)
_register(r"\bespa[çc]o\b.*\b(?:livre|usado|dispon[ií]vel)\b", "espaco_disco", _no_args)
_register(r"\b(?:quanto|quanta)\b.*\b(?:armazenamento|disco|espa[çc]o)\b", "espaco_disco", _no_args)

# ---------------------------------------------------------------------------
# Info rede
# ---------------------------------------------------------------------------
_register(r"\bipconfig\b", "info_rede", _no_args)
_register(r"\binfo(?:rma[çc][õo]es?)?\b.*\brede\b", "info_rede", _no_args)
_register(r"\brede\b.*\binfo\b", "info_rede", _no_args)
_register(r"\bconex[ãa]o\b.*\brede\b", "info_rede", _no_args)
_register(r"\bconfigurar?[çc][ãa]o\b.*\brede\b", "info_rede", _no_args)
_register(r"\badaptador(?:es)?\b.*\brede\b", "info_rede", _no_args)

# ---------------------------------------------------------------------------
# Excluir arquivo
# ---------------------------------------------------------------------------
def _extract_excluir(match) -> dict:
    text = match.string.strip()

    nome_m = re.search(
        r"arquivo\s+(?:de\s+texto\s+)?(?:\.txt\s+)?(?:chamad[ao]\s+)?['\"]?([a-zA-Z0-9\u00C0-\u024F_.\-]+)",
        text, re.IGNORECASE,
    )
    if not nome_m:
        nome_m = re.search(
            r"(?:chamad[ao]|com\s+(?:o\s+)?nome)\s+['\"]?([a-zA-Z0-9\u00C0-\u024F_.\-]+)",
            text, re.IGNORECASE,
        )
    if not nome_m:
        return None

    nome = nome_m.group(1).strip().strip("'\"")
    stopwords = {"no", "na", "do", "da", "dentro", "em", "desktop", "um", "uma", "de", "chamado", "chamada"}
    if nome.lower() in stopwords:
        return None

    result = {"nome": nome}

    dir_m = re.search(
        r"(?:dentro\s+d[ao]|n[ao]|d[ao])\s+pasta\s+['\"]?([a-zA-Z0-9\u00C0-\u024F_ -]+?)(?:['\"]?\s*(?:d[ao]\s+|$))",
        text, re.IGNORECASE,
    )
    if dir_m:
        dir_name = dir_m.group(1).strip()
        if dir_name.lower() not in {"área", "area", "trabalho", "desktop"}:
            result["diretorio"] = dir_name

    return result

_register(r"\b(?:exclu|apag|delet|remov|elimin)(?:ir|a|e|ar|indo)\b[^.]*\barquivo\b", "excluir_arquivo", _extract_excluir)
_register(r"\barquivo\b.*\b(?:exclu|apag|delet|remov|elimin)", "excluir_arquivo", _extract_excluir)


# ---------------------------------------------------------------------------
# Ações bloqueadas (interceptar ANTES de cair no Ollama)
# ---------------------------------------------------------------------------
BLOCKED_PATTERNS: list[tuple[re.Pattern, str]] = []


def _block(pattern: str, message: str):
    BLOCKED_PATTERNS.append((re.compile(pattern, re.IGNORECASE), message))


_block(
    r"\b(?:exclu|apag|delet|remov|elimin)(?:ir|a|e|ar|indo)\b.*\b(?:pasta|diret[oó]rio)\b",
    "Não posso excluir pastas por razões de segurança. Você pode fazer isso manualmente pelo Explorador de Arquivos.",
)
_block(
    r"\b(?:pasta|diret[oó]rio)\b.*\b(?:exclu|apag|delet|remov|elimin)",
    "Não posso excluir pastas por razões de segurança. Você pode fazer isso manualmente pelo Explorador de Arquivos.",
)
_block(
    r"\bdesinstala(?:r|e)\b",
    "Não posso desinstalar aplicativos por razões de segurança.",
)
_block(
    r"\b(?:registro|regedit)\b",
    "Não posso acessar ou editar o registro do Windows por razões de segurança.",
)
_block(
    r"\bformata(?:r|e)\b.*\b(?:disco|hd|ssd|unidade|partição)\b",
    "Não posso formatar discos por razões de segurança.",
)
_block(
    r"\b(?:desliga|reinicia|restart|shutdown)\b.*\b(?:computador|pc|m[aá]quina|sistema)\b",
    "Não posso desligar ou reiniciar o computador por razões de segurança.",
)
_block(
    r"\bexecut(?:ar|e)\b.*\b(?:powershell|cmd|comando|script)\b",
    "Não posso executar comandos ou scripts arbitrários por razões de segurança. Utilize as ferramentas disponíveis.",
)


def match_blocked(message: str) -> str | None:
    text = message.strip()
    for pattern, msg in BLOCKED_PATTERNS:
        if pattern.search(text):
            return msg
    return None


def match_intent(message: str) -> tuple[str, dict] | None:
    text = message.strip()
    for pattern, tool_name, extract_fn in PATTERNS:
        m = pattern.search(text)
        if m:
            args = extract_fn(m)
            if args is None:
                continue
            return tool_name, args
    return None
