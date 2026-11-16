# MCP Local

Exemplos de servidores e clientes MCP usando [FastMCP](https://gofastmcp.com).

## Exemplos

| Pasta | Transporte | Descrição |
|-------|------------|-----------|
| `src/mcp_local/` | stdio | O cliente inicia o servidor como subprocesso e chama a tool `dar_bom_dia`. |
| `src/mcp_remoto/` | HTTP (porta 8000) | O servidor roda separado e o cliente se conecta pela URL. Tool `dar_boa_noite`. |
| `src/mcp_wiki/` | HTTP (porta 8001) | Tools de busca na Wikipedia. O cliente envia o resumo a um LLM (Groq) para gerar a resposta. |

## Requisitos

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)
- Para o exemplo `mcp_wiki`: uma chave de API do [Groq](https://console.groq.com)

## Configuração

```powershell
uv sync
```

Para o `mcp_wiki`, crie um arquivo `.env` na raiz a partir do modelo e preencha a chave:

```powershell
Copy-Item .env.example .env
```

O `.env` está no `.gitignore` e nunca deve ser enviado ao repositório.

## Como executar

**mcp_local** (um terminal só):

```powershell
uv run src/mcp_local/cliente.py
```

**mcp_remoto** e **mcp_wiki** (dois terminais: servidor primeiro, cliente depois):

```powershell
# terminal 1
uv run src/mcp_wiki/servidor.py

# terminal 2
uv run src/mcp_wiki/cliente.py
```

Troque `mcp_wiki` por `mcp_remoto` para o outro exemplo. Os servidores usam portas diferentes, então podem rodar ao mesmo tempo.
