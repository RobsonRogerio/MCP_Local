"""Servidor MCP da Wikipedia para uso no Claude Desktop (transporte stdio).

Diferença para o servidor.py:
    O servidor.py roda em HTTP e é iniciado manualmente (usado pelo cliente.py).
    Este arquivo roda em stdio: o próprio Claude Desktop inicia o programa e
    conversa com ele pela entrada/saída padrão, sem abrir porta de rede.

Como usar:
    Não é preciso rodar manualmente. Ele é iniciado pelo Claude Desktop,
    conforme o arquivo claude_desktop_config_example.json.

Atenção: em stdio, nada deve ser impresso na saída padrão (print), pois isso
quebra a comunicação com o Claude Desktop.
"""

# [1] Imports: biblioteca padrão primeiro, depois bibliotecas de terceiros
# em ordem alfabética (convenção PEP 8).
from typing import Annotated

import wikipedia
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from pydantic import Field

# [2] Aqui não há HOST nem PORTA: em stdio o servidor não escuta na rede.
# [3] Define o idioma da Wikipedia. Sem isso, a biblioteca busca em inglês.
wikipedia.set_lang("pt")

# [4] Cria o servidor. O nome aparece para os clientes que se conectam.
servidor_mcp = FastMCP("mcp-busca-wikipedia")


# [5] O decorador @servidor_mcp.tool() transforma a função em uma tool MCP.
# Três coisas viram a "documentação" que o LLM lê para decidir como usar a tool:
#   - o nome da função
#   - o docstring (texto entre aspas triplas)
#   - a descrição de cada parâmetro (Annotated + Field)
@servidor_mcp.tool()
def buscar_wikipedia_local(
    busca: Annotated[str, Field(description="Termo a pesquisar na Wikipedia")],
) -> list[str]:
    """Busca artigos na Wikipedia em português e retorna os títulos mais relevantes."""
    try:
        return wikipedia.search(busca)
    except Exception as erro:
        # [6] Se a Wikipedia estiver fora do ar ou sem internet, a biblioteca
        # lança várias exceções diferentes. Capturamos todas e lançamos um
        # ToolError: é o erro "oficial" do MCP, e o cliente recebe a mensagem
        # em vez de um erro interno confuso.
        raise ToolError(f"Falha ao buscar na Wikipedia: {erro}") from erro


# [7] Segunda tool: a busca devolve só títulos, então esta devolve o conteúdo.
# O LLM consegue combinar as duas: primeiro busca, depois resume.
@servidor_mcp.tool()
def resumir_artigo(
    titulo: Annotated[str, Field(description="Título exato de um artigo da Wikipedia")],
) -> str:
    """Retorna um resumo de três frases de um artigo da Wikipedia."""
    try:
        # auto_suggest=False: usa o título exatamente como foi enviado, sem
        # a biblioteca "adivinhar" outro artigo parecido.
        return wikipedia.summary(titulo, sentences=3, auto_suggest=False)
    except wikipedia.DisambiguationError as erro:
        # [8] Título ambíguo (ex.: "Mercúrio" = planeta, elemento, deus...).
        # erro.options traz as opções; mostramos só as 5 primeiras.
        opcoes = ", ".join(erro.options[:5])
        raise ToolError(f"Título ambíguo. Algumas opções: {opcoes}") from erro
    except wikipedia.PageError as erro:
        raise ToolError(f"Nenhum artigo encontrado com o título '{titulo}'.") from erro
    except Exception as erro:
        raise ToolError(f"Falha ao obter o resumo: {erro}") from erro


# [9] Só executa quando o arquivo é rodado diretamente (é o que o Claude Desktop faz).
if __name__ == "__main__":
    servidor_mcp.run(transport="stdio")
