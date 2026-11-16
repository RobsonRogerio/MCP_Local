import asyncio
from pathlib import Path

from fastmcp import Client

CAMINHO_SERVIDOR = Path(__file__).parent / "servidor.py"


async def testar_servidor(nome_usuario: str, id_usuario: int) -> None:
    async with Client(CAMINHO_SERVIDOR) as cliente:
        resultado = await cliente.call_tool(
            "dar_bom_dia",
            arguments={"nome_usuario": nome_usuario, "id_usuario": id_usuario},
        )
        print(f"Resultado obtido do servidor MCP: {resultado.data}")


if __name__ == "__main__":
    asyncio.run(testar_servidor(nome_usuario="Robson", id_usuario=4))
