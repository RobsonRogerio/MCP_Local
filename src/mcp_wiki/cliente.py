"""Cliente que busca na Wikipedia via MCP e pede a um LLM para explicar o resultado.

Fluxo:
    1. Conecta ao servidor MCP e chama as tools de busca e de resumo.
    2. Envia o resumo ao LLM (Groq) para gerar uma resposta amigável.

Como rodar (o servidor precisa estar no ar em outro terminal):
    uv run src/mcp_wiki/servidor.py     # terminal 1
    uv run src/mcp_wiki/cliente.py      # terminal 2
"""

# [1] Imports: biblioteca padrão, depois terceiros em ordem alfabética.
import asyncio
import os
import sys

import dotenv
from fastmcp import Client
from fastmcp.exceptions import ToolError
from openai import APIError, OpenAI

# [2] Configurações em constantes no topo, fáceis de achar e trocar.
URL_SERVIDOR = "http://127.0.0.1:8001/mcp"  # mesma porta do servidor.py
GROQ_URL = "https://api.groq.com/openai/v1"  # o Groq aceita o SDK da OpenAI
MODELO = "openai/gpt-oss-20b"  # se for descontinuado, liste os modelos da sua conta


def encerrar_com_erro(mensagem: str) -> None:
    """Mostra a mensagem no canal de erro (stderr) e encerra com código 1."""
    # Código de saída diferente de 0 sinaliza falha para o sistema operacional.
    print(mensagem, file=sys.stderr)
    sys.exit(1)


# [3] Parte MCP: fala com o servidor. É "async" porque o cliente MCP usa
# operações de rede assíncronas (por isso o "await" nas chamadas).
async def consultar_wikipedia(busca: str) -> tuple[str, str]:
    """Busca o termo no servidor MCP e devolve (título do artigo, resumo)."""
    try:
        # [4] "async with" abre a conexão e garante que ela feche no final.
        # Se o servidor estiver desligado, o FastMCP lança RuntimeError aqui.
        async with Client(URL_SERVIDOR) as cliente:
            try:
                # [5] call_tool(nome_da_tool, argumentos) executa a tool no servidor.
                # .data traz o retorno já convertido para tipos Python.
                resultado = await cliente.call_tool(
                    "buscar_na_wikipedia", arguments={"busca": busca}
                )
                titulos = resultado.data
                if not titulos:
                    encerrar_com_erro(f"Nenhum artigo encontrado para '{busca}'.")

                # Usamos o primeiro título, o mais relevante, para pedir o resumo.
                titulo = titulos[0]
                resumo = await cliente.call_tool(
                    "resumir_artigo", arguments={"titulo": titulo}
                )
                return titulo, resumo.data
            except ToolError as erro:
                # [6] ToolError = a tool executou, mas devolveu uma falha
                # (ex.: artigo não encontrado). Diferente de falha de conexão.
                encerrar_com_erro(f"A tool retornou um erro: {erro}")
    except RuntimeError as erro:
        # Só chega aqui se a conexão falhar: os erros das tools já foram
        # tratados acima.
        encerrar_com_erro(
            f"Não foi possível conectar ao servidor em {URL_SERVIDOR}: {erro}\n"
            "Inicie o servidor antes com: uv run src/mcp_wiki/servidor.py"
        )


# [7] Parte LLM: é uma função comum (sem async). Ela roda DEPOIS que a conexão
# MCP foi fechada, então não mantemos o servidor ocupado enquanto o LLM pensa.
def gerar_resposta(busca: str, titulo: str, resumo: str) -> str:
    """Pede ao LLM uma resposta amigável baseada no resumo da Wikipedia."""
    # [8] A chave de API vem do arquivo .env (que não vai para o Git).
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        encerrar_com_erro(
            "Variável GROQ_API_KEY não encontrada. "
            "Crie um arquivo .env (veja o .env.example)."
        )

    # [9] Usamos o SDK da OpenAI apontando para o Groq via base_url.
    cliente_llm = OpenAI(api_key=api_key, base_url=GROQ_URL)

    # [10] Dois papéis de mensagem:
    #   - "system": instruções fixas de comportamento do modelo
    #   - "user": o pedido concreto, com o tema e o conteúdo da Wikipedia
    mensagem_sistema = (
        "Você é um assistente que responde com base em trechos da Wikipedia. "
        "Use apenas as informações fornecidas e responda de forma amigável, "
        "em português."
    )
    mensagem_usuario = (
        f"Tema pesquisado: {busca}\n\n"
        f"Resumo do artigo '{titulo}':\n{resumo}\n\n"
        "Fale mais sobre o assunto."
    )

    try:
        resposta = cliente_llm.chat.completions.create(
            model=MODELO,
            messages=[
                {"role": "system", "content": mensagem_sistema},
                {"role": "user", "content": mensagem_usuario},
            ],
        )
    except APIError as erro:
        # [11] APIError cobre falhas da API: modelo inexistente, chave
        # inválida, limite de uso, rede etc.
        encerrar_com_erro(f"Erro ao chamar o LLM: {erro}")

    return resposta.choices[0].message.content


def main(busca: str) -> None:
    # [12] load_dotenv() lê o arquivo .env e coloca as variáveis no ambiente.
    dotenv.load_dotenv()

    # asyncio.run() executa a função async e espera o resultado.
    titulo, resumo = asyncio.run(consultar_wikipedia(busca))
    print(f"Artigo encontrado: {titulo}\n")
    print(gerar_resposta(busca, titulo, resumo))


# [13] Só executa quando o arquivo é rodado diretamente.
if __name__ == "__main__":
    main(busca="El Nino")
