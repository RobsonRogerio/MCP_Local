from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

servidor_mcp = FastMCP("mcp-remoto")


@servidor_mcp.tool()
def dar_boa_noite(
    nome_usuario: Annotated[str, Field(description="Nome do usuário a ser saudado")],
    id_usuario: Annotated[int, Field(description="Identificador do usuário")],
) -> str:
    """Retorna uma saudação personalizada para o usuário."""
    return f"Boa noite, {nome_usuario} (ID: {id_usuario})"


if __name__ == "__main__":
    servidor_mcp.run(transport="http", host="127.0.0.1", port=8000)