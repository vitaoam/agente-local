import httpx

from app.config import OLLAMA_BASE_URL, OLLAMA_MODEL, DESKTOP_PATH, DOCUMENTS_PATH, DOWNLOADS_PATH

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "obter_ip",
            "description": "Retorna o endereço IP local da máquina do usuário.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "listar_desktop",
            "description": "Lista todos os arquivos e pastas da Área de Trabalho do usuário.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "criar_pasta_desktop",
            "description": "Cria uma nova pasta na Área de Trabalho do usuário. Requer confirmação.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nome": {"type": "string", "description": "Nome da pasta a ser criada"}
                },
                "required": ["nome"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "mover_arquivo",
            "description": (
                "Move um arquivo de um local para outro, dentro das pastas permitidas "
                "(Desktop, Documents, Downloads). Requer confirmação."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "origem": {
                        "type": "string",
                        "description": "Caminho completo do arquivo de origem",
                    },
                    "destino": {
                        "type": "string",
                        "description": "Caminho completo do destino (pasta ou arquivo)",
                    },
                },
                "required": ["origem", "destino"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "renomear_arquivo",
            "description": (
                "Renomeia um arquivo em locais permitidos do usuário "
                "(Desktop, Documents, Downloads). Requer confirmação."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "caminho": {
                        "type": "string",
                        "description": "Caminho completo do arquivo a ser renomeado",
                    },
                    "novo_nome": {
                        "type": "string",
                        "description": "Novo nome do arquivo (apenas o nome, sem caminho)",
                    },
                },
                "required": ["caminho", "novo_nome"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "abrir_app",
            "description": (
                "Abre um aplicativo pelo nome amigável. "
                "Apps suportados: paint, bloco de notas, notepad, calculadora, "
                "explorer, edge, navegador, terminal, cmd, powershell, configurações."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "nome_app": {
                        "type": "string",
                        "description": "Nome amigável do aplicativo a abrir",
                    }
                },
                "required": ["nome_app"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "obter_hora_atual",
            "description": "Retorna a data e hora atual formatada em português.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "ping_host",
            "description": "Faz ping em uma máquina ou endereço IP.",
            "parameters": {
                "type": "object",
                "properties": {
                    "host": {"type": "string", "description": "Nome da máquina ou IP"}
                },
                "required": ["host"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "info_rede",
            "description": "Mostra informações de rede (ipconfig).",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "verificar_processo",
            "description": "Verifica se um processo/aplicativo está em execução.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nome": {"type": "string", "description": "Nome do processo ou aplicativo"}
                },
                "required": ["nome"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "listar_processos",
            "description": "Lista os processos em execução no computador.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "fechar_processo",
            "description": "Encerra/fecha um processo em execução. Requer confirmação.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nome": {"type": "string", "description": "Nome do processo a encerrar"}
                },
                "required": ["nome"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "info_sistema",
            "description": "Mostra informações do sistema (CPU, RAM, hostname, versão do Windows).",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "espaco_disco",
            "description": "Mostra o espaço em disco (livre/usado) de cada unidade.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]

SYSTEM_PROMPT = f"""Assistente local Windows 11. Responda em português do Brasil. Use APENAS as ferramentas fornecidas. Nunca invente comandos.

Pastas do usuário:
- Desktop: {DESKTOP_PATH}
- Documents: {DOCUMENTS_PATH}
- Downloads: {DOWNLOADS_PATH}

Se o pedido estiver fora do escopo, recuse educadamente. Não apague arquivos nem execute comandos administrativos."""


class OllamaClient:
    def __init__(self, base_url: str = OLLAMA_BASE_URL, model: str = OLLAMA_MODEL):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = httpx.Timeout(120.0, connect=10.0)

    async def check_health(self) -> dict:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    model_names = [m.get("name", "") for m in models]
                    model_base = self.model.split(":")[0]
                    model_installed = any(
                        self.model in name or name.startswith(model_base)
                        for name in model_names
                    )
                    return {
                        "ollama_online": True,
                        "model_configured": self.model,
                        "model_installed": model_installed,
                        "models_available": model_names,
                    }
            return {"ollama_online": False, "error": "Resposta inesperada do Ollama."}
        except httpx.ConnectError:
            return {
                "ollama_online": False,
                "error": "Ollama não está rodando. Execute 'ollama serve' no terminal.",
            }
        except Exception as e:
            return {"ollama_online": False, "error": str(e)}

    async def chat(self, messages: list[dict], use_tools: bool = True) -> dict:
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": 0.1, "num_ctx": 2048},
        }
        if use_tools:
            payload["tools"] = TOOL_DEFINITIONS

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/chat", json=payload
                )
                if response.status_code == 200:
                    return response.json()

                error_text = response.text
                if "not found" in error_text.lower():
                    return {
                        "error": True,
                        "message": (
                            f"O modelo '{self.model}' não foi encontrado. "
                            f"Execute: ollama pull {self.model}"
                        ),
                    }
                return {"error": True, "message": f"Erro do Ollama: {error_text}"}
        except httpx.ConnectError:
            return {
                "error": True,
                "message": (
                    "Não foi possível conectar ao Ollama. "
                    "Verifique se ele está rodando com 'ollama serve'."
                ),
            }
        except httpx.TimeoutException:
            return {
                "error": True,
                "message": "O Ollama demorou muito para responder. Tente novamente.",
            }
        except Exception as e:
            return {"error": True, "message": f"Erro inesperado: {e}"}


ollama_client = OllamaClient()
