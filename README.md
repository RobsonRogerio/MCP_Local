# MCP Local

Exemplos de servidores e clientes MCP usando [FastMCP](https://gofastmcp.com).

## Exemplos

| Pasta | Transporte | Descrição |
|-------|------------|-----------|
| `src/mcp_local/` | stdio | O cliente inicia o servidor como subprocesso e chama a tool `dar_bom_dia`. |
| `src/mcp_remoto/` | HTTP (porta 8000) | O servidor roda separado e o cliente se conecta pela URL. Tool `dar_boa_noite`. |
| `src/mcp_wiki/` | HTTP (porta 8001) | Tools de busca na Wikipedia. O cliente envia o resumo a um LLM (Groq) para gerar a resposta. |
| `src/mcp_wiki/servidor_claude_wiki.py` | stdio | Mesmo servidor da Wikipedia, para uso no Claude Desktop. |

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

## Usar o servidor da Wikipedia no Claude Desktop

O Claude Desktop inicia o servidor por conta própria e conversa com ele via stdio. Por isso ele usa o arquivo `src/mcp_wiki/servidor_claude_wiki.py`, e não o `servidor.py` (HTTP). Não é preciso rodar nada manualmente nem ter a chave do Groq: no Claude Desktop, o próprio Claude responde.

1. Abra o `claude_desktop_config_example.json` e ajuste os caminhos para o seu computador:
   - `command`: caminho completo do `uv.exe` (descubra com `(Get-Command uv).Source` no PowerShell).
   - `--directory`: caminho da pasta deste projeto.
2. No Claude Desktop, abra **Configurações → Desenvolvedor → Editar configuração**. Isso abre o `claude_desktop_config.json` real.
3. Copie o bloco `busca-wikipedia` para dentro de `mcpServers`. Se o arquivo já tiver outros servidores, adicione o bloco sem apagar os existentes.
4. Feche o Claude Desktop por completo, inclusive o ícone da bandeja, e abra de novo.
5. Peça algo como "busque na Wikipedia sobre Inteligência artificial". O Claude deve pedir permissão para usar as tools `buscar_wikipedia_local` e `resumir_artigo`.

**Problemas comuns:**

- O servidor não aparece na lista: confira os logs em `%APPDATA%\Claude\logs\` (arquivo `mcp-server-busca-wikipedia.log`) e se os caminhos do JSON estão corretos. Use barras `/` ou barras duplas `\\` nos caminhos.
- Erro de "Acesso negado" no `.venv`: feche outros servidores do projeto que estejam rodando no terminal antes de abrir o Claude Desktop.
- Para testar o servidor fora do Claude Desktop, rode o `cliente.py` com o `servidor.py` (veja a seção "Como executar").
