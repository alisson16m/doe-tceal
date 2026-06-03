import pytest
from unittest.mock import patch, MagicMock
from scripts.extrair_texto import extrair_texto, extrair_metadados


def test_extrair_texto_retorna_string():
    pdf_bytes = b"%PDF-1.4 fake"
    pagina_mock = MagicMock()
    pagina_mock.extract_text.return_value = "Tribunal de Contas\nEdição Nº 14420"

    with patch("scripts.extrair_texto.pdfplumber.open") as mock_open:
        mock_pdf = MagicMock()
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=False)
        mock_pdf.pages = [pagina_mock]
        mock_open.return_value = mock_pdf

        resultado = extrair_texto(pdf_bytes)

    assert "Tribunal de Contas" in resultado
    assert isinstance(resultado, str)


def test_extrair_texto_pagina_sem_texto():
    pdf_bytes = b"%PDF-1.4 fake"
    pagina_mock = MagicMock()
    pagina_mock.extract_text.return_value = None  # pdfplumber retorna None quando vazio

    with patch("scripts.extrair_texto.pdfplumber.open") as mock_open:
        mock_pdf = MagicMock()
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=False)
        mock_pdf.pages = [pagina_mock]
        mock_open.return_value = mock_pdf

        resultado = extrair_texto(pdf_bytes)

    assert resultado == ""


def test_extrair_metadados_com_data():
    texto = "Maceió, 02 de junho de 2026\nEdição Nº 14419"
    meta = extrair_metadados(texto)
    assert meta["data"] == "2026-06-02"
    assert meta["data_formatada"] == "02/06/2026"
    assert meta["numero_edicao"] == "14419"


def test_extrair_metadados_sem_correspondencia():
    texto = "Texto sem data nem número de edição reconhecível"
    meta = extrair_metadados(texto)
    assert meta["data"] is None
    assert meta["data_formatada"] is None
    assert meta["numero_edicao"] is None
