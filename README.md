# Agente Local — Windows 11

Assistente de linguagem natural **100% local** para Windows 11. Recebe comandos em português do Brasil, interpreta a intenção e executa ações controladas no computador — sem nuvem, sem API paga, sem telemetria.

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688)
![Ollama](https://img.shields.io/badge/Ollama-LLM%20Local-black)
![Windows 11](https://img.shields.io/badge/Windows-11-0078D6)

## Visão Geral

O Agente Local é um aplicativo web que roda inteiramente na sua máquina. Você digita pedidos em português e ele executa ações reais no sistema operacional:

- Consultar IP e informações de rede
- Pingar máquinas na rede
- Verificar, listar e encerrar processos
- Consultar informações do sistema (RAM, CPU, disco)
- Listar arquivos da Área de Trabalho
- Criar pastas, mover e renomear arquivos
- Abrir aplicativos
- Consultar data e hora

**Nenhum dado sai do seu computador.**

## Como Funciona

O agente usa uma arquitetura híbrida para ser rápido e confiável:

1. **Intent Matcher local** — reconhece padrões comuns via regex e executa a ferramenta instantaneamente, sem chamar nenhum modelo de IA
2. **Ollama (fallback)** — para pedidos complexos que o matcher não reconhece, envia ao modelo local via Ollama

Na prática, a maioria dos comandos é resolvida em milissegundos pelo matcher local. O modelo só é acionado para frases ambíguas ou fora dos padrões conhecidos.

## Arquitetura

```
agente-local/
├── app/
│   ├── main.py                    # Aplicação FastAPI
│   ├── config.py                  # Configurações centrais
│   ├── models/
│   │   └── schemas.py             # Schemas Pydantic
│   ├── services/
│   │   ├── agent.py               # Lógica principal do agente
│   │   ├── intent_matcher.py      # Reconhecimento local de intenções
│   │   ├── ollama_client.py       # Cliente HTTP para Ollama
│   │   ├── confirmation_store.py  # Ações pendentes em memória
│   │   ├── app_registry.py        # Catálogo de apps suportados
│   │   ├── path_guard.py          # Validação de caminhos seguros
│   │   └── powershell_runner.py   # Execução controlada de PowerShell
│   ├── tools/
│   │   ├── system_tools.py        # IP, hora, info sistema, disco
│   │   ├── file_tools.py          # Listar, criar, mover, renomear
│   │   ├── app_tools.py           # Abrir aplicativos
│   │   ├── network_tools.py       # Ping, ipconfig
│   │   └── process_tools.py       # Verificar, listar, fechar processos
│   ├── routers/
│   │   ├── chat.py                # Endpoints de chat
│   │   └── health.py              # Health check
│   ├── static/
│   │   ├── style.css
│   │   └── app.js
│   └── templates/
│       └── index.html
├── tests/
│   ├── test_path_guard.py
│   ├── test_app_registry.py
│   └── test_tools_basic.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Requisitos

- **Windows 11**
- **Python 3.11+**
- **Ollama** instalado e rodando localmente

## Sobre o Modelo de IA

O modelo é usado apenas como fallback para pedidos que o matcher local não reconhece. O padrão configurado é o **`qwen2.5:1.5b`**, escolhido por ser leve e rodar bem em máquinas com pouca RAM.

| Modelo | Tamanho | RAM mínima | Velocidade em CPU |
|---|---|---|---|
| `qwen2.5:1.5b` (padrão) | ~1 GB | ~4 GB | Rápido (2-5s) |
| `qwen2.5:3b` | ~2 GB | ~6 GB | Moderado (5-10s) |
| `qwen2.5:7b` | ~4.7 GB | ~8 GB | Lento (10-20s) |

Para trocar o modelo, defina a variável de ambiente antes de iniciar:

```powershell
$env:OLLAMA_MODEL = "qwen2.5:3b"
```

## Instalação

### 1. Clonar o repositório

```powershell
git clone https://github.com/seu-usuario/agente-local.git
cd agente-local
```

### 2. Instalar dependências Python

```powershell
pip install -r requirements.txt
```

### 3. Instalar o Ollama

Baixe e instale em: https://ollama.com/download

### 4. Baixar o modelo

```powershell
ollama pull qwen2.5:1.5b
```

## Como Executar

### 1. Iniciar o Ollama

```powershell
ollama serve
```

Mantenha este terminal aberto.

### 2. Iniciar o Agente

Em **outro** terminal:

```powershell
cd agente-local
uvicorn app.main:app --reload
```

### 3. Acessar a Interface

Abra o navegador em: **http://localhost:8000**

## Exemplos de Uso

### Rede

| Comando | O que faz |
|---|---|
| "qual é o meu ip?" | Mostra hostname e IP local |
| "pinga a máquina SERVIDOR01" | Executa ping para a máquina |
| "ping 192.168.1.1" | Ping por IP |
| "ipconfig" | Mostra configuração de rede |
| "informações de rede" | Mesmo que ipconfig |

### Processos

| Comando | O que faz |
|---|---|
| "o chrome está rodando?" | Verifica se o processo está ativo |
| "o ollama está executando?" | Verifica processo do Ollama |
| "quais processos estão rodando?" | Lista os top 25 processos |
| "feche o notepad" | Encerra o processo (pede confirmação) |

### Sistema

| Comando | O que faz |
|---|---|
| "informações do sistema" | CPU, RAM, hostname, versão do Windows |
| "quanta RAM tenho?" | Mostra uso de memória |
| "espaço em disco" | Espaço livre/usado por unidade |

### Arquivos

| Comando | O que faz |
|---|---|
| "quais arquivos estão no desktop?" | Lista a Área de Trabalho |
| "crie uma pasta chamada Projetos" | Cria pasta (pede confirmação) |
| "renomeie teste.txt para teste2.txt" | Renomeia (pede confirmação) |
| "mova relatorio.pdf para Documents" | Move arquivo (pede confirmação) |

### Aplicativos

| Comando | O que faz |
|---|---|
| "abra o Paint" | Abre o Microsoft Paint |
| "abra a calculadora" | Abre a Calculadora |
| "abra o bloco de notas" | Abre o Notepad |

### Geral

| Comando | O que faz |
|---|---|
| "que horas são?" | Data e hora atual em português |
| "que dia é hoje?" | Mesmo que acima |

## Ferramentas Disponíveis (14)

| Ferramenta | Confirmação | Descrição |
|---|---|---|
| `obter_ip` | Não | IP e hostname local |
| `obter_hora_atual` | Não | Data e hora em português |
| `info_sistema` | Não | CPU, RAM, hostname, Windows |
| `espaco_disco` | Não | Espaço livre/usado por unidade |
| `info_rede` | Não | Configuração de rede (ipconfig) |
| `ping_host` | Não | Ping em máquina/IP |
| `verificar_processo` | Não | Verifica se processo está ativo |
| `listar_processos` | Não | Lista processos em execução |
| `listar_desktop` | Não | Arquivos da Área de Trabalho |
| `abrir_app` | Não | Abre aplicativo por nome |
| `criar_pasta_desktop` | **Sim** | Cria pasta no Desktop |
| `mover_arquivo` | **Sim** | Move arquivo entre pastas permitidas |
| `renomear_arquivo` | **Sim** | Renomeia arquivo |
| `fechar_processo` | **Sim** | Encerra um processo |

## Aplicativos Suportados

| Nome amigável | Executável |
|---|---|
| paint | mspaint |
| bloco de notas / notepad | notepad |
| calculadora | calc |
| explorer / explorador | explorer |
| edge / navegador | msedge |
| terminal | wt |
| cmd | cmd |
| powershell | powershell |
| configurações | ms-settings: |

## Endpoints da API

| Método | Rota | Descrição |
|---|---|---|
| GET | `/` | Interface web |
| GET | `/health` | Status do servidor e do Ollama |
| POST | `/chat` | Envia mensagem ao agente |
| POST | `/confirm` | Confirma ação pendente |
| POST | `/cancel` | Cancela ação pendente |

## Segurança

O projeto foi desenhado com segurança como prioridade:

- **Sem execução livre de comandos** — o agente só pode usar ferramentas pré-definidas
- **Pastas restritas** — operações de arquivo limitadas a Desktop, Documents e Downloads
- **Confirmação obrigatória** — ações destrutivas exigem confirmação explícita
- **Sem exclusão de arquivos** — o agente não pode apagar nada
- **Sem privilégios elevados** — opera apenas no contexto do usuário atual
- **Processos protegidos** — processos críticos do sistema não podem ser encerrados
- **Validação de caminhos** — todos os caminhos são normalizados e verificados
- **Sanitização de inputs** — hostnames e nomes de processos são validados contra injeção
- **PowerShell controlado** — quando usado, tem timeout e lista de bloqueio

### O agente NÃO pode:

- Apagar arquivos ou pastas
- Editar o registro do Windows
- Desinstalar aplicativos
- Executar comandos administrativos
- Acessar pastas fora do escopo permitido
- Encerrar processos críticos do sistema (csrss, svchost, explorer, etc.)
- Usar `Invoke-Expression` ou comandos equivalentes

## Testes

```powershell
pytest tests/ -v
```

## Limitações

- Sem histórico de conversa entre sessões
- Sem autenticação (uso exclusivamente local)
- Sem banco de dados
- Catálogo de aplicativos limitado ao que está registrado
- Operações de arquivo restritas a Desktop, Documents e Downloads
- Se a pasta Desktop tiver nome localizado diferente de "Desktop", pode ser necessário ajuste no `config.py`
- Modelo pequeno pode não entender pedidos muito complexos (mas o matcher local cobre os casos comuns)

## Próximos Passos

- [ ] Histórico de conversa persistente
- [ ] Streaming de respostas do modelo
- [ ] Mais ferramentas (busca de arquivos, clipboard, screenshots, etc.)
- [ ] Catálogo expandido de aplicativos
- [ ] Interface com temas (claro/escuro)
- [ ] Logs de auditoria das ações executadas
- [ ] Containerização com Docker

## Licença

Este projeto é de uso livre. Sinta-se à vontade para usar, modificar e distribuir.
