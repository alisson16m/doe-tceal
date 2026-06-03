import os
import sys
from datetime import date, timedelta

from scripts.descobrir_edicao import buscar_edicao_especifica, buscar_edicoes_novas, ler_estado, salvar_estado
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

    id_forcado = os.environ.get("INPUT_ID_EDICAO", "").strip()

    if id_forcado:
        try:
            id_num = int(id_forcado)
        except ValueError:
            print(f"ERRO: ID inválido: '{id_forcado}'. Informe apenas o número (ex: 14418).", file=sys.stderr)
            sys.exit(1)
        print(f"Modo manual: buscando edição {id_num}...")
        resultado = buscar_edicao_especifica(id_num)
        if resultado is None:
            print(f"Edição {id_num} não encontrada no servidor. Verifique o ID e tente novamente.")
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

    maior_id_processado = estado["ultimo_id"] if not id_forcado else 0

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

    if atualizar_estado:
        salvar_estado({"ultimo_id": maior_id_processado})
        print(f"\nConcluído. Novo último ID: {maior_id_processado}")
    else:
        print(f"\nConcluído. Estado não alterado (processamento manual).")


if __name__ == "__main__":
    main()
