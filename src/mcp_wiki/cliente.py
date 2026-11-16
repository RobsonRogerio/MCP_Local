import asyncio
import sys
import os
import dotenv

from openai import OpenAI
from fastmcp import Client

URL_SERVIDOR = "http://127.0.0.1:8001/mcp"


async def testar_servidor(busca: str) -> None:
    dotenv.load_dotenv()
    api_key = os.environ['GROQ_API_KEY']
    try:
        async with Client(URL_SERVIDOR) as cliente:
            resultado = await cliente.call_tool(
                "buscar_na_wikipedia",
                arguments={"busca": busca},
            )
            print(resultado)
            mensagem_sistema = f"""
            Você é um bot que faz buscas na wikipedia. O usuário buscou pelo tema: {busca}.
            Resultados da busca na Wikipedia: {resultado.data}
            Com base nesse conteúdo devolva uma resposta amigável ao usuário.
            """

            cliente_llm = OpenAI(
                api_key=api_key,
                base_url="https://api.groq.com/openai/v1",
            )
            response = cliente_llm.chat.completions.create(
                model='openai/gpt-oss-20b',
                messages=[
                    {"role": "system", "content": mensagem_sistema},
                    {"role": "user", "content": "Fale mais sobre o assunto"},
                ],
            )
            print(response.choices[0].message.content)

    except RuntimeError as erro:
        print(
            f"Não foi possível conectar ao servidor em {URL_SERVIDOR}: {erro}\n"
            "Inicie o servidor antes com: uv run src/mcp_wiki/servidor.py",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(testar_servidor(busca="Inteligência artificial"))
