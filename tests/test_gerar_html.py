import pytest
import json
from pathlib import Path
from scripts.gerar_html import salvar_edicao, regenerar_index

DADOS_EDICAO = {
    "id": 14420,
    "data": "2026-06-03",
    "data_formatada": "03/06/2026",
    "url_pdf": "https://doe.tceal.tc.br/api/api/editions/viewPdf/14420",
    "resumo_geral": "Edição com 1 resolução e 2 acórdãos.",
    "normativos": [
        {"tipo": "Resolução", "numero": "TC-0045/2026", "resumo": "Aprova normas de TI."}
    ],
    "decisoes": [
        {"tipo": "Acórdão", "numero": "0123/2026", "resumo": "Contas aprovadas."},
        {"tipo": "Acórdão", "numero": "0124/2026", "resumo": "Contas reprovadas."},
    ],
    "atos_administrativos": [],
    "outros": [],
}


def test_salvar_edicao_cria_html(tmp_path, monkeypatch):
    monkeypatch.setattr("scripts.gerar_html.EDICOES_DIR", tmp_path / "edicoes")
    monkeypatch.setattr("scripts.gerar_html.DADOS_DIR", tmp_path / "dados")
    monkeypatch.setattr("scripts.gerar_html.INDEX_PATH", tmp_path / "index.html")

    salvar_edicao(DADOS_EDICAO)

    html_path = tmp_path / "edicoes" / "14420.html"
    assert html_path.exists()
    conteudo = html_path.read_text(encoding="utf-8")
    assert "03/06/2026" in conteudo
    assert "TC-0045/2026" in conteudo
    assert "Acórdão" in conteudo


def test_salvar_edicao_cria_json(tmp_path, monkeypatch):
    monkeypatch.setattr("scripts.gerar_html.EDICOES_DIR", tmp_path / "edicoes")
    monkeypatch.setattr("scripts.gerar_html.DADOS_DIR", tmp_path / "dados")
    monkeypatch.setattr("scripts.gerar_html.INDEX_PATH", tmp_path / "index.html")

    salvar_edicao(DADOS_EDICAO)

    json_path = tmp_path / "dados" / "14420.json"
    assert json_path.exists()
    dados = json.loads(json_path.read_text(encoding="utf-8"))
    assert dados["id"] == 14420
    assert len(dados["decisoes"]) == 2


def test_regenerar_index_lista_edicoes(tmp_path, monkeypatch):
    monkeypatch.setattr("scripts.gerar_html.EDICOES_DIR", tmp_path / "edicoes")
    monkeypatch.setattr("scripts.gerar_html.DADOS_DIR", tmp_path / "dados")
    monkeypatch.setattr("scripts.gerar_html.INDEX_PATH", tmp_path / "index.html")

    # Pre-populate dados dir with a JSON file
    dados_dir = tmp_path / "dados"
    dados_dir.mkdir()
    (dados_dir / "14420.json").write_text(
        json.dumps(DADOS_EDICAO), encoding="utf-8"
    )

    regenerar_index()

    index_html = tmp_path / "index.html"
    assert index_html.exists()
    conteudo = index_html.read_text(encoding="utf-8")
    assert "14420" in conteudo
    assert "03/06/2026" in conteudo


def test_regenerar_index_vazio(tmp_path, monkeypatch):
    monkeypatch.setattr("scripts.gerar_html.EDICOES_DIR", tmp_path / "edicoes")
    monkeypatch.setattr("scripts.gerar_html.DADOS_DIR", tmp_path / "dados")
    monkeypatch.setattr("scripts.gerar_html.INDEX_PATH", tmp_path / "index.html")
    (tmp_path / "dados").mkdir()

    regenerar_index()

    conteudo = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert "Nenhuma edição processada" in conteudo
