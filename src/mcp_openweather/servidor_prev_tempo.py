import os
import dotenv
import requests

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

dotenv.load_dotenv()
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
if not OPENWEATHER_API_KEY:
    # SystemExit com texto encerra o programa e mostra a mensagem no stderr,
    # sem o traceback longo de um KeyError.
    raise SystemExit(
        "Variável OPENWEATHER_API_KEY não encontrada. "
        "Crie um arquivo .env (veja o .env.example)."
    )

servidor_mcp = FastMCP('mcp-previsao-tempo')


@servidor_mcp.tool()
def buscar_tempo_atual(local: str) -> dict:
    """Retorna o tempo atual de uma cidade (ex.: São Paulo)."""
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": local,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric",
        "lang": "pt_br"
    }
    try:
        response = requests.get(url=url, params=params, timeout=15)
        response.raise_for_status()
    except requests.HTTPError as erro:
        status = erro.response.status_code
        if status == 404:
            raise ToolError(f"Cidade '{local}' não encontrada.") from None
        if status == 401:
            raise ToolError("Chave de API do OpenWeather inválida.") from None
        raise ToolError(f"O OpenWeather retornou o erro HTTP {status}.") from None
    except requests.RequestException:
        raise ToolError("Não foi possível conectar ao OpenWeather.") from None
    return response.json()


@servidor_mcp.tool()
def buscar_previsao_tempo(local: str) -> dict:
    """Retorna a previsão do tempo de uma cidade (ex.: São Paulo)."""
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": local,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric",
        "lang": "pt_br",
        "cnt": 8
    }
    try:
        response = requests.get(url=url, params=params, timeout=15)
        response.raise_for_status()
    except requests.HTTPError as erro:
        status = erro.response.status_code
        if status == 404:
            raise ToolError(f"Cidade '{local}' não encontrada.") from None
        if status == 401:
            raise ToolError("Chave de API do OpenWeather inválida.") from None
        raise ToolError(f"O OpenWeather retornou o erro HTTP {status}.") from None
    except requests.RequestException:
        raise ToolError("Não foi possível conectar ao OpenWeather.") from None
    return response.json()


if __name__ == "__main__":
    servidor_mcp.run(transport="http", host="127.0.0.1", port=8002)
