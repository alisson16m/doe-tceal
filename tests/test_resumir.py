import pytest
import json
from unittest.mock import patch, MagicMock
from scripts.resumir import resumir_edicao, PROMPT_TEMPLATE


RESPOSTA_GEMINI_VALIDA = {
    "resumo_geral": "Edição com 2 acórdãos e 1 resolução.",
    "normativos": [
        {
            "tipo": "Resolução",
            "numero": "TC-0045/2026",
            "ementa": "Aprova normas de fiscalização",
            "resumo": "Estabelece procedimentos para auditorias de TI."
        }
    ],
    "decisoes": [
        {
            "tipo": "Acórdão",
            "numero": "0123/2026",
            "processo": "TC-0001/2026",
            "interessados": "Prefeitura de Maceió",
            "relator": "Conselheiro Fulano",
            "resumo": "Julgou regular a prestação de contas."
        }
    ],
    "atos_administrativos": [],
    "outros": []
}


def test_resumir_edicao_retorna_dict_estruturado():
    texto = "Texto do diário oficial para teste"
    metadados = {"data": "2026-06-02", "data_formatada": "02/06/2026", "numero_edicao": "14419"}
    api_key = "chave-de-teste"

    resposta_mock = MagicMock()
    resposta_mock.text = json.dumps(RESPOSTA_GEMINI_VALIDA)

    with patch("scripts.resumir.genai.GenerativeModel") as mock_model_cls:
        mock_model = MagicMock()
        mock_model.generate_content.return_value = resposta_mock
        mock_model_cls.return_value = mock_model

        resultado = resumir_edicao(texto, metadados, api_key)

    assert resultado["resumo_geral"] == "Edição com 2 acórdãos e 1 resolução."
    assert len(resultado["normativos"]) == 1
    assert resultado["normativos"][0]["numero"] == "TC-0045/2026"
    assert resultado["decisoes"][0]["tipo"] == "Acórdão"
    assert resultado["atos_administrativos"] == []


def test_resumir_edicao_inclui_metadados():
    texto = "Texto do diário"
    metadados = {"data": "2026-06-02", "data_formatada": "02/06/2026", "numero_edicao": "14419"}
    api_key = "chave-de-teste"

    resposta_mock = MagicMock()
    resposta_mock.text = json.dumps(RESPOSTA_GEMINI_VALIDA)

    with patch("scripts.resumir.genai.GenerativeModel") as mock_model_cls:
        mock_model = MagicMock()
        mock_model.generate_content.return_value = resposta_mock
        mock_model_cls.return_value = mock_model

        resultado = resumir_edicao(texto, metadados, api_key)

    assert resultado["data"] == "2026-06-02"
    assert resultado["data_formatada"] == "02/06/2026"


def test_resumir_edicao_erro_json():
    texto = "Texto do diário"
    metadados = {"data": "2026-06-02", "data_formatada": "02/06/2026", "numero_edicao": "14419"}
    api_key = "chave-de-teste"

    resposta_mock = MagicMock()
    resposta_mock.text = "Resposta inválida não é JSON"

    with patch("scripts.resumir.genai.GenerativeModel") as mock_model_cls:
        mock_model = MagicMock()
        mock_model.generate_content.return_value = resposta_mock
        mock_model_cls.return_value = mock_model

        with pytest.raises(ValueError, match="Gemini retornou resposta inválida"):
            resumir_edicao(texto, metadados, api_key)
