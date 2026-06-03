import json
import os
import sys
from datetime import date, timedelta

from scripts.descobrir_edicao import (
    buscar_edicao_especifica,
    buscar_edicoes_novas,
    estimar_id_para_data,
    ler_estado,
    salvar_estado,
)
from scripts.extrair_texto import extrair_metadados, extrair_texto
from scripts.gerar_html import DADOS_DIR, salvar_edicao
from scripts.resumir import resumir_edicao


def data_de_ontem() -> str:
    return (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")


def data_formatada_de_ontem() -> str:
    return (date.today() - timedelta(days=1)).strftime("%d/%m/%Y")


def _parsear_data(texto: str) -> str:
    """Parse date string in DD/MM/AAAA or YYYY-MM-DD format. Returns YYYY-MM-DD."""
    texto = texto.strip()
    if "/" in texto:
        partes = texto.split("/")
        if len(partes) == 3:
            d, m, a = partes
            return f"{a.zfill(4)}-{m.zfill(2)}-{d.zfill(2)}"
    date.fromisoformat(texto)  # valida formato YYYY-MM-DD
    return texto


def _buscar_edicao_por_data(data_iso: str) -> tuple[int, bytes] | None:
    """Find edition PDF for a given date (YYYY-MM-DD).

    First checks existing dados/*.json, then probes IDs around an estimate.
    """
    # Verifica se já temos um JSON com essa data
    for f in sorted(DADOS_DIR.glob("*.json")):
        if f.name == "estado.json":
            continue
        d = json.loads(f.read_text(encoding="utf-8"))
        if d.get("data") == data_iso:
            print(f"  Data encontrada nos dados existentes: edição {d['id']}.")
            resultado = buscar_edicao_especifica(d["id"])
            if resultado:
                return resultado

    # Estima o ID e tenta IDs em torno da estimativa
    alvo = date.fromisoformat(data_iso)
    estimado = estimar_id_para_data(alvo)
    print(f"  ID estimado para {data_iso}: {estimado}. Verificando candidatos...")

    for offset in sorted(range(-6, 7), key=abs):
        candidato = estimado + offset
        if candidato <= 0:
            continue
        resultado = buscar_edicao_especifica(candidato)
        if resultado is None:
            continue
        texto = extrair_texto(resultado[1])
        metadados = extrair_metadados(texto)
        data_encontrada = metadados.get("data", "")
        if data_encontrada == data_iso:
            print(f"  Confirmado: edição {candidato} corresponde a {data_iso}.")
            return resultado
        print(f"  ID {candidato} é da data {data_encontrada or '?'}. Tentando próximo...")

    return None


def main() -> None:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERRO: variável de ambiente GEMINI_API_KEY não definida.", file=sys.stderr)
        sys.exit(1)

    data_forcada = os.environ.get("INPUT_DATA_EDICAO", "").strip()

    if data_forcada:
        try:
            data_iso = _parsear_data(data_forcada)
        except (ValueError, IndexError):
            print(
                f"ERRO: data inválida '{data_forcada}'. Use o formato DD/MM/AAAA.",
                file=sys.stderr,
            )
            sys.exit(1)

        print(f"Modo manual: buscando edição de {data_forcada}...")
        resultado = _buscar_edicao_por_data(data_iso)
        if resultado is None:
            print(
                f"Edição para {data_forcada} não encontrada. "
                "Verifique se é um dia útil com publicação."
            )
            return
        edicoes = [resultado]
        atualizar_estado = False
    else:
        estado = ler_estado()
        print(f"Último ID processado: {estado['ultimo_id']}")
        edicoes = buscar_edicoes_novas(estado)
        if not edicoes:
            print("Nenhuma edição nova encontrada. Encerrando.")
            return
        atualizar_estado = True

    print(f"{len(edicoes)} edição(ões) encontrada(s): {[e[0] for e in edicoes]}")

    maior_id_processado = 0
    if atualizar_estado:
        maior_id_processado = estado["ultimo_id"]

    for edicao_id, pdf_bytes in edicoes:
        print(f"\nProcessando edição {edicao_id}...")

        texto = extrair_texto(pdf_bytes)
        if not texto.strip():
            print(f"  AVISO: nenhum texto extraído do PDF {edicao_id}. Pulando.")
            continue

        metadados = extrair_metadados(texto)

        if not metadados["data"]:
            metadados["data"] = data_de_ontem()
            metadados["data_formatada"] = data_formatada_de_ontem()
            print("  Aviso: data não encontrada no PDF. Usando data de ontem como fallback.")

        print(f"  Data: {metadados['data_formatada']}")
        print("  Enviando ao Gemini...")

        dados_resumo = resumir_edicao(texto, metadados, api_key)
        dados_resumo["id"] = edicao_id

        salvar_edicao(dados_resumo)
        print(f"  ✓ Edição {edicao_id} salva.")

        maior_id_processado = max(maior_id_processado, edicao_id)

    if atualizar_estado:
        salvar_estado({"ultimo_id": maior_id_processado})
        print(f"\nConcluído. Novo último ID: {maior_id_processado}")
    else:
        print("\nConcluído. Estado não alterado (processamento manual).")


if __name__ == "__main__":
    main()
