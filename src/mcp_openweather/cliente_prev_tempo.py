"""Cliente que busca informações sobre o clima pela api OpenWeather via MCP e pede a um LLM para exibir o resultado.

Fluxo:
    1. Conecta ao servidor MCP e chama as tools de buscar informações sobre o tempo atual e previsão do tempo.
    2. Envia o resumo ao LLM (Groq) para gerar uma resposta amigável.

Como rodar (o servidor precisa estar no ar em outro terminal):
    uv run src/mcp_openweather/servidor_prev_tempo.py     # terminal 1
    uv run src/mcp_openweather/cliente_prev_tempo.py      # terminal 2

Para escolher a cidade, passe-a como argumento (entre aspas se tiver espaço):
    uv run src/mcp_openweather/cliente_prev_tempo.py "São Paulo"
"""

# [1] Imports: biblioteca padrão, depois terceiros em ordem alfabética.
import asyncio
import json
import os
import sys
from typing import NoReturn

import dotenv
from fastmcp import Client
from fastmcp.exceptions import ToolError
from openai import APIError, OpenAI

# [2] Configurações em constantes no topo, fáceis de achar e trocar.
URL_SERVIDOR = "http://127.0.0.1:8002/mcp"  # mesma porta do servidor MCP
GROQ_URL = "https://api.groq.com/openai/v1"  # o Groq aceita o SDK da OpenAI
MODELO = "openai/gpt-oss-20b"  # se for descontinuado, liste os modelos da sua conta


def encerrar_com_erro(mensagem: str) -> NoReturn:
    """Mostra a mensagem no canal de erro (stderr) e encerra com código 1."""
    # NoReturn avisa o editor que esta função nunca retorna (sempre encerra o
    # programa). Assim ele sabe que o código depois de chamá-la não executa.
    # Código de saída diferente de 0 sinaliza falha para o sistema operacional.
    print(mensagem, file=sys.stderr)
    sys.exit(1)


# [3] Parte MCP: fala com o servidor. É "async" porque o cliente MCP usa
# operações de rede assíncronas (por isso o "await" nas chamadas).
async def consultar_open_weather(local: str) -> tuple[dict, dict]:
    """Consulta o servidor MCP e devolve (tempo atual, previsão do tempo)."""
    try:
        # [4] "async with" abre a conexão e garante que ela feche no final.
        # Se o servidor estiver desligado, o FastMCP lança RuntimeError aqui.
        async with Client(URL_SERVIDOR) as cliente:
            try:
                # [5] call_tool(nome_da_tool, argumentos) executa a tool no servidor.
                # .data traz o retorno já convertido para tipos Python.
                tempo_atual = await cliente.call_tool(
                    "buscar_tempo_atual", arguments={"local": local}
                )
                previsao_tempo = await cliente.call_tool(
                    "buscar_previsao_tempo", arguments={"local": local}
                )
                return tempo_atual.data, previsao_tempo.data
            except ToolError as erro:
                # [6] ToolError = a tool executou, mas devolveu uma falha
                # (ex.: local não encontrado). Diferente de falha de conexão.
                encerrar_com_erro(f"A tool retornou um erro: {erro}")
    except RuntimeError as erro:
        # Só chega aqui se a conexão falhar: os erros das tools já foram
        # tratados acima.
        encerrar_com_erro(
            f"Não foi possível conectar ao servidor em {URL_SERVIDOR}: {erro}\n"
            "Inicie o servidor antes com: uv run src/mcp_openweather/servidor_prev_tempo.py"
        )


# [7] Parte LLM: é uma função comum (sem async). Ela roda DEPOIS que a conexão
# MCP foi fechada, então não mantemos o servidor ocupado enquanto o LLM pensa.
def gerar_resposta(local: str, tempo_atual: dict, previsao: dict) -> str:
    """Pede ao LLM uma resposta amigável baseada no retorno do Open Weather."""
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
    #   - "user": o pedido concreto, sobre a previsão do tempo
    mensagem_sistema = (
        "Você é um assistente que interpreta informações de clima e tempo provenientes da API do OpenWeather. "
        "Responda de forma objetiva, em português."
    )
    mensagem_usuario = (
        f"Local pesquisado: {local}\n\n"
        f"Tempo atual (JSON): {json.dumps(tempo_atual, ensure_ascii=False)}\n\n"
        f"Previsão (JSON): {json.dumps(previsao, ensure_ascii=False)}\n\n"
        "Resuma o tempo atual e a previsão das próximas horas."
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


def main(local: str) -> None:
    # [12] load_dotenv() lê o arquivo .env e coloca as variáveis no ambiente.
    dotenv.load_dotenv()

    # asyncio.run() executa a função async e espera o resultado.
    tempo_atual, previsao = asyncio.run(consultar_open_weather(local))
    print(gerar_resposta(local, tempo_atual, previsao))


# [13] Só executa quando o arquivo é rodado diretamente.
if __name__ == "__main__":
    # sys.argv é a lista de argumentos da linha de comando: sys.argv[0] é o
    # nome do script e sys.argv[1] é o primeiro argumento (a cidade, se houver).
    # Sem argumento, usa "Atibaia" como padrão.
    cidade = sys.argv[1] if len(sys.argv) > 1 else "Atibaia"
    main(local=cidade)
