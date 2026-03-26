import json

from app.services.ollama_client import ollama_client, SYSTEM_PROMPT
from app.services.confirmation_store import confirmation_store
from app.services.intent_matcher import match_intent
from app.config import TOOLS_REQUIRING_CONFIRMATION
from app.tools.system_tools import obter_ip, obter_hora_atual, info_sistema, espaco_disco
from app.tools.file_tools import (
    listar_desktop,
    criar_pasta_desktop,
    mover_arquivo,
    renomear_arquivo,
)
from app.tools.app_tools import abrir_app
from app.tools.network_tools import ping_host, info_rede
from app.tools.process_tools import verificar_processo, listar_processos, fechar_processo

TOOL_MAP = {
    "obter_ip": obter_ip,
    "obter_hora_atual": obter_hora_atual,
    "info_sistema": info_sistema,
    "espaco_disco": espaco_disco,
    "listar_desktop": listar_desktop,
    "criar_pasta_desktop": criar_pasta_desktop,
    "mover_arquivo": mover_arquivo,
    "renomear_arquivo": renomear_arquivo,
    "abrir_app": abrir_app,
    "ping_host": ping_host,
    "info_rede": info_rede,
    "verificar_processo": verificar_processo,
    "listar_processos": listar_processos,
    "fechar_processo": fechar_processo,
}

CONFIRMATION_DESCRIPTIONS = {
    "criar_pasta_desktop": lambda args: (
        f"Criar a pasta '{args.get('nome', '?')}' na Área de Trabalho"
    ),
    "mover_arquivo": lambda args: (
        f"Mover '{args.get('origem', '?')}' para '{args.get('destino', '?')}'"
    ),
    "renomear_arquivo": lambda args: (
        f"Renomear '{args.get('caminho', '?')}' para '{args.get('novo_nome', '?')}'"
    ),
    "fechar_processo": lambda args: (
        f"Encerrar o processo '{args.get('nome', '?')}'"
    ),
}


def execute_tool(tool_name: str, tool_args: dict) -> dict:
    func = TOOL_MAP.get(tool_name)
    if not func:
        return {"success": False, "message": f"Ferramenta '{tool_name}' não encontrada."}
    try:
        return func(**tool_args)
    except TypeError as e:
        return {"success": False, "message": f"Parâmetros inválidos para '{tool_name}': {e}"}
    except Exception as e:
        return {"success": False, "message": f"Erro ao executar '{tool_name}': {e}"}


def _build_response(tool_name: str, tool_args: dict) -> dict:
    if tool_name in TOOLS_REQUIRING_CONFIRMATION:
        desc_func = CONFIRMATION_DESCRIPTIONS.get(tool_name)
        description = desc_func(tool_args) if desc_func else f"Executar {tool_name}"
        action_id = confirmation_store.create(tool_name, tool_args, description)
        return {
            "type": "confirmation",
            "message": f"Confirmação necessária: {description}.\n\nDeseja prosseguir?",
            "action_id": action_id,
        }

    result = execute_tool(tool_name, tool_args)
    icon = "✅" if result.get("success") else "❌"
    return {
        "type": "response",
        "message": f"{icon} {result.get('message', 'Ação executada.')}",
    }


async def process_message(user_message: str) -> dict:
    # 1) Tentar resolver localmente por padrões conhecidos (instantâneo)
    local_match = match_intent(user_message)
    if local_match:
        tool_name, tool_args = local_match
        if tool_name in TOOL_MAP:
            return _build_response(tool_name, tool_args)

    # 2) Fallback: perguntar ao modelo via Ollama
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    response = await ollama_client.chat(messages)

    if response.get("error"):
        return {"type": "error", "message": response["message"]}

    message = response.get("message", {})
    tool_calls = message.get("tool_calls")

    if not tool_calls:
        content = message.get("content", "")
        if not content:
            return {
                "type": "response",
                "message": "Não entendi o pedido. Pode reformular?",
            }
        return {"type": "response", "message": content}

    tool_call = tool_calls[0]
    func_info = tool_call.get("function", {})
    tool_name = func_info.get("name", "")
    tool_args = func_info.get("arguments", {})

    if isinstance(tool_args, str):
        try:
            tool_args = json.loads(tool_args)
        except json.JSONDecodeError:
            tool_args = {}

    if tool_name not in TOOL_MAP:
        return {
            "type": "response",
            "message": f"Ferramenta '{tool_name}' não está disponível.",
        }

    return _build_response(tool_name, tool_args)


async def confirm_action(action_id: str) -> dict:
    action = confirmation_store.get(action_id)
    if not action:
        return {
            "type": "error",
            "message": "Ação pendente não encontrada ou já expirou.",
        }

    result = execute_tool(action.tool_name, action.tool_args)
    confirmation_store.remove(action_id)

    icon = "✅" if result.get("success") else "❌"
    return {
        "type": "response",
        "message": f"{icon} {result.get('message', 'Ação executada.')}",
    }


async def cancel_action(action_id: str) -> dict:
    action = confirmation_store.get(action_id)
    if not action:
        return {
            "type": "error",
            "message": "Ação pendente não encontrada ou já expirou.",
        }

    confirmation_store.remove(action_id)
    return {"type": "response", "message": "Ação cancelada pelo usuário."}
