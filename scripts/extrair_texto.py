import io
import re
from datetime import datetime
import pdfplumber

MESES = {
    "janeiro": 1, "fevereiro": 2, "março": 3, "abril": 4,
    "maio": 5, "junho": 6, "julho": 7, "agosto": 8,
    "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12,
}


def extrair_texto(pdf_bytes: bytes) -> str:
    """Extract and concatenate text from all PDF pages."""
    paginas = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for pagina in pdf.pages:
            texto = pagina.extract_text()
            if texto:
                paginas.append(texto)
    return "\n".join(paginas)


def extrair_metadados(texto: str) -> dict:
    """Extract publication date and edition number from the gazette header text."""
    trecho = texto[:3000]

    padrao_data = r"(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})"
    match_data = re.search(padrao_data, trecho, re.IGNORECASE)

    padrao_edicao = r"[Ee]di[çc][ãa]o\s+[Nn][ºo°.]\s*(\d+)"
    match_edicao = re.search(padrao_edicao, trecho, re.IGNORECASE)

    data_str = None
    data_formatada = None

    if match_data:
        dia = int(match_data.group(1))
        mes_nome = match_data.group(2).lower()
        ano = int(match_data.group(3))
        mes = MESES.get(mes_nome)
        if mes:
            try:
                data = datetime(ano, mes, dia)
                data_str = data.strftime("%Y-%m-%d")
                data_formatada = data.strftime("%d/%m/%Y")
            except ValueError:
                pass

    return {
        "data": data_str,
        "data_formatada": data_formatada,
        "numero_edicao": match_edicao.group(1) if match_edicao else None,
    }
