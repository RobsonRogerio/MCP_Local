import asyncio
import sys

from fastmcp import Client

URL_SERVIDOR = "http://127.0.0.1:8000/mcp"


async def testar_servidor(nome_usuario: str, id_usuario: int) -> None:
    try:
        async with Client(URL_SERVIDOR) as cliente:
            resultado = await cliente.call_tool(
                "dar_boa_noite",
                arguments={"nome_usuario": nome_usuario, "id_usuario": id_usuario},
            )
            print(f"Resultado obtido do servidor MCP: {resultado.data}")
    except RuntimeError as erro:
        print(
            f"Não foi possível conectar ao servidor em {URL_SERVIDOR}: {erro}\n"
            "Inicie o servidor antes com: uv run src/mcp_remoto/servidor.py",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(testar_servidor(nome_usuario="Robson", id_usuario=10))
