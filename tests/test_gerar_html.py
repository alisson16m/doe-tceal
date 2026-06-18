import json
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
        {
            "tipo": "Acórdão",
            "numero": "0123/2026",
            "processo": "TC Nº 0001/2026",
            "assunto": "Prestação de Contas Anual",
            "interessados": "Prefeitura de Maceió",
            "secao": "Conselheiro Fulano de Tal",
            "resumo": "Contas aprovadas.",
        },
        {
            "tipo": "Decisão Monocrática",
            "numero": "0124/2026",
            "processo": "TC Nº 4911/2023",
            "assunto": "Auxílio Pensão Por Morte",
            "interessados": "João Batista de Lima Santos",
            "secao": "Conselheira Rosa Maria Ribeiro de Albuquerque",
            "resumo": "Registro do ato de concessão de pensão por morte.",
        },
    ],
    "atos_administrativos": [
        {
            "tipo": "Despacho",
            "processo": "TC/12.001398/2025",
            "assunto": "Aposentadoria por Invalidez",
            "interessado": "Rodoval Roque dos Santos",
            "secao": "Conselheiro Rodrigo Siqueira Cavalcante",
            "resumo": "Remetidos os autos à Diretoria-Geral.",
        }
    ],
    "outros": [],
}

DADOS_EDICAO_KPIS = {
    "id": 14421,
    "data": "2026-06-04",
    "data_formatada": "04/06/2026",
    "url_pdf": "https://doe.tceal.tc.br/api/api/editions/viewPdf/14421",
    "resumo_geral": "Edição de teste para KPIs.",
    "normativos": [
        {"tipo": "Resolução", "numero": "TC-0046/2026", "resumo": "Norma X."}
    ],
    "decisoes": [
        {"tipo": "Acórdão", "numero": "0200/2026", "processo": "TC-200/2026",
         "assunto": "Contas", "interessados": "Prefeitura Y", "resumo": "Aprovado."},
        {"tipo": "Acórdão", "numero": "0201/2026", "processo": "TC-201/2026",
         "assunto": "Contas", "interessados": "Prefeitura Z", "resumo": "Reprovado."},
        {"tipo": "Decisão Monocrática", "numero": "0202/2026", "processo": "TC-202/2026",
         "assunto": "Pensão", "interessados": "João", "resumo": "Registro."},
        {"tipo": "Parecer Prévio", "numero": "0203/2026", "processo": "TC-203/2026",
         "assunto": "Contas de Governo", "interessados": "Prefeito X", "resumo": "Favorável."},
    ],
    "atos_administrativos": [
        {"tipo": "Parecer Ministerial", "numero": "PAR-001/2026", "processo": "TC-204/2026",
         "assunto": "Representação", "interessado": "Órgão A", "resumo": "Admissível."},
        {"tipo": "Parecer Ministerial", "numero": "PAR-002/2026", "processo": "TC-205/2026",
         "assunto": "Representação", "interessado": "Órgão B", "resumo": "Inadmissível."},
        {"tipo": "Despacho", "processo": "TC-206/2026",
         "assunto": "Remessa", "interessado": "Entidade C", "resumo": "Remetido."},
        {"tipo": "Portaria", "numero": "PORT-001/2026", "processo": "TC-207/2026",
         "assunto": "Nomeação", "interessado": "Servidor D", "resumo": "Nomeado."},
    ],
    "outros": [
        {"tipo": "Aviso de Licitação", "resumo": "Pregão eletrônico nº 001/2026."}
    ],
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


def test_regenerar_index_dados_grafico_ordenado_cronologicamente(tmp_path, monkeypatch):
    monkeypatch.setattr("scripts.gerar_html.EDICOES_DIR", tmp_path / "edicoes")
    monkeypatch.setattr("scripts.gerar_html.DADOS_DIR", tmp_path / "dados")
    monkeypatch.setattr("scripts.gerar_html.INDEX_PATH", tmp_path / "index.html")

    dados_dir = tmp_path / "dados"
    dados_dir.mkdir()
    (dados_dir / "14420.json").write_text(
        json.dumps(DADOS_EDICAO), encoding="utf-8"
    )
    (dados_dir / "14421.json").write_text(
        json.dumps(DADOS_EDICAO_KPIS), encoding="utf-8"
    )

    regenerar_index()

    conteudo = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert "grafico-decisoes" in conteudo
    # Extrair o JSON dos dados do gráfico e verificar ordem cronológica
    import re
    match = re.search(r"const dadosGrafico = (\[.*?\]);", conteudo, re.DOTALL)
    assert match, "JSON de dados_grafico não encontrado no HTML"
    dados = json.loads(match.group(1))
    assert len(dados) == 2
    assert dados[0]["data"] == "2026-06-03"
    assert dados[1]["data"] == "2026-06-04"


def test_regenerar_index_dados_grafico_contagens_corretas(tmp_path, monkeypatch):
    monkeypatch.setattr("scripts.gerar_html.EDICOES_DIR", tmp_path / "edicoes")
    monkeypatch.setattr("scripts.gerar_html.DADOS_DIR", tmp_path / "dados")
    monkeypatch.setattr("scripts.gerar_html.INDEX_PATH", tmp_path / "index.html")

    dados_dir = tmp_path / "dados"
    dados_dir.mkdir()
    (dados_dir / "14421.json").write_text(
        json.dumps(DADOS_EDICAO_KPIS), encoding="utf-8"
    )

    regenerar_index()

    conteudo = (tmp_path / "index.html").read_text(encoding="utf-8")
    # DADOS_EDICAO_KPIS tem: 2 acórdãos, 1 monocrática, 1 parecer prévio
    assert '"acordaos": 2' in conteudo
    assert '"monocraticas": 1' in conteudo
    assert '"previos": 1' in conteudo


def test_regenerar_index_grafico_nao_aparece_sem_edicoes(tmp_path, monkeypatch):
    monkeypatch.setattr("scripts.gerar_html.EDICOES_DIR", tmp_path / "edicoes")
    monkeypatch.setattr("scripts.gerar_html.DADOS_DIR", tmp_path / "dados")
    monkeypatch.setattr("scripts.gerar_html.INDEX_PATH", tmp_path / "index.html")
    (tmp_path / "dados").mkdir()

    regenerar_index()

    conteudo = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert "grafico-decisoes" not in conteudo


def test_regenerar_index_kpis_por_tipo(tmp_path, monkeypatch):
    monkeypatch.setattr("scripts.gerar_html.EDICOES_DIR", tmp_path / "edicoes")
    monkeypatch.setattr("scripts.gerar_html.DADOS_DIR", tmp_path / "dados")
    monkeypatch.setattr("scripts.gerar_html.INDEX_PATH", tmp_path / "index.html")

    dados_dir = tmp_path / "dados"
    dados_dir.mkdir()
    (dados_dir / "14421.json").write_text(
        json.dumps(DADOS_EDICAO_KPIS), encoding="utf-8"
    )

    regenerar_index()

    conteudo = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert "1 normativo(s)" in conteudo
    assert "2 acórdão(s)" in conteudo
    assert "1 dec. monocrática(s)" in conteudo
    assert "1 parecer(es) prévio(s)" in conteudo
    assert "2 parecer(es)" in conteudo
    assert "3 outro(s)" in conteudo  # Despacho + Portaria + Aviso de Licitação
