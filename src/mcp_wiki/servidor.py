"""Servidor MCP que oferece buscas na Wikipedia como "tools".

O que é um servidor MCP?
    Um programa que publica funções (chamadas de "tools") para que um
    cliente, como um LLM, possa descobri-las e executá-las.

Como rodar:
    uv run src/mcp_wiki/servidor.py
"""

# [1] Imports: biblioteca padrão primeiro, depois bibliotecas de terceiros
# em ordem alfabética (convenção PEP 8).
from typing import Annotated

import wikipedia
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from pydantic import Field

# [2] Configurações do servidor em constantes no topo do arquivo.
# O cliente precisa usar o mesmo endereço, então ficam fáceis de achar.
# A porta 8001 evita conflito com o servidor do exemplo mcp_remoto (8000).
HOST = "127.0.0.1"
PORTA = 8001

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
def buscar_na_wikipedia(
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


# [9] Só executa quando rodamos este arquivo diretamente (não quando importado).
# transport="http" faz o servidor escutar em http://HOST:PORTA/mcp
if __name__ == "__main__":
    servidor_mcp.run(transport="http", host=HOST, port=PORTA)
