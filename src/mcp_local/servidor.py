from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

servidor_mcp = FastMCP("mcp-teste")


@servidor_mcp.tool()
def dar_bom_dia(
    nome_usuario: Annotated[str, Field(description="Nome do usuário a ser saudado")],
    id_usuario: Annotated[int, Field(description="Identificador do usuário")],
) -> str:
    """Retorna uma saudação personalizada para o usuário."""
    return f"Bom dia, {nome_usuario} (ID: {id_usuario})"


if __name__ == "__main__":
    servidor_mcp.run()
