# MCP Local

Exemplo de servidor e cliente MCP locais usando [FastMCP](https://gofastmcp.com).

- `src/mcp_local/servidor.py`: servidor MCP com a tool `dar_bom_dia`.
- `src/mcp_local/cliente.py`: cliente que inicia o servidor via stdio e chama a tool.

## Requisitos

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)

## Como executar

```powershell
uv sync
uv run src/mcp_local/cliente.py
```
