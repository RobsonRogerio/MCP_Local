from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field
import wikipedia

servidor_mcp = FastMCP("mcp-busca-wikipedia")

@servidor_mcp.tool()
def buscar_na_wikipedia(
    busca: Annotated[str, Field(description="Termo a pesquisar na Wikipedia")],
) -> list[str]:
    """Busca artigos na Wikipedia em português e retorna os títulos mais relevantes."""
    return wikipedia.search(busca)


if __name__ == "__main__":
    servidor_mcp.run(transport="http", host="127.0.0.1", port=8001)
