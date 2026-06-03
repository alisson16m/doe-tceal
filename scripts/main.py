import os
import sys
from datetime import date, timedelta

from scripts.descobrir_edicao import buscar_edicoes_novas, ler_estado, salvar_estado
from scripts.extrair_texto import extrair_texto, extrair_metadados
from scripts.resumir import resumir_edicao
from scripts.gerar_html import salvar_edicao


def data_de_ontem() -> str:
    return (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")


def data_formatada_de_ontem() -> str:
    return (date.today() - timedelta(days=1)).strftime("%d/%m/%Y")


def main() -> None:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERRO: variável de ambiente GEMINI_API_KEY não definida.", file=sys.stderr)
        sys.exit(1)

    estado = ler_estado()
    print(f"Último ID processado: {estado['ultimo_id']}")

    edicoes = buscar_edicoes_novas(estado)

    if not edicoes:
        print("Nenhuma edição nova encontrada. Encerrando.")
        return

    print(f"{len(edicoes)} edição(ões) nova(s) encontrada(s): {[e[0] for e in edicoes]}")

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
        print(f"  Enviando ao Gemini...")

        dados_resumo = resumir_edicao(texto, metadados, api_key)
        dados_resumo["id"] = edicao_id

        salvar_edicao(dados_resumo)
        print(f"  ✓ Edição {edicao_id} salva.")

        maior_id_processado = max(maior_id_processado, edicao_id)

    salvar_estado({"ultimo_id": maior_id_processado})
    print(f"\nConcluído. Novo último ID: {maior_id_processado}")


if __name__ == "__main__":
    main()
