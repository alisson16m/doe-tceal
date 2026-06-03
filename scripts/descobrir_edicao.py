import json
import requests
from datetime import date
from pathlib import Path

BASE_URL = "https://doe.tceal.tc.br/api/api/editions/viewPdf"
ESTADO_PATH = Path("dados/estado.json")
MAX_TENTATIVAS = 5

# Ponto de ancoragem para estimativa de IDs por data
_ANCORA_DATA = date(2026, 6, 2)
_ANCORA_ID = 14419


def ler_estado() -> dict:
    if ESTADO_PATH.exists():
        return json.loads(ESTADO_PATH.read_text(encoding="utf-8"))
    return {"ultimo_id": 14419}


def salvar_estado(estado: dict) -> None:
    ESTADO_PATH.parent.mkdir(exist_ok=True)
    ESTADO_PATH.write_text(
        json.dumps(estado, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def buscar_edicao_especifica(id_edicao: int) -> tuple[int, bytes] | None:
    """Download a specific edition by ID. Returns (id, pdf_bytes) or None if not found."""
    url = f"{BASE_URL}/{id_edicao}"
    try:
        resposta = requests.get(url, timeout=30)
        if resposta.status_code == 200 and resposta.content.startswith(b"%PDF"):
            return (id_edicao, resposta.content)
    except requests.RequestException:
        pass
    return None


def estimar_id_para_data(data_alvo: date) -> int:
    """Estimate the edition ID for a given date using the sequential anchor point."""
    delta = (data_alvo - _ANCORA_DATA).days
    return max(1, _ANCORA_ID + round(delta * 5 / 7))


def buscar_edicoes_novas(estado: dict) -> list[tuple[int, bytes]]:
    """Probe sequential IDs after the last known one. Returns (id, pdf_bytes) pairs."""
    ultimo_id = estado["ultimo_id"]
    encontradas = []

    for i in range(1, MAX_TENTATIVAS + 1):
        candidato = ultimo_id + i
        url = f"{BASE_URL}/{candidato}"
        try:
            resposta = requests.get(url, timeout=30)
        except requests.RequestException:
            break

        if resposta.status_code == 200 and resposta.content.startswith(b"%PDF"):
            encontradas.append((candidato, resposta.content))
        else:
            if encontradas:
                break

    return encontradas
