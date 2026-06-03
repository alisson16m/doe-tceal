import pytest
from unittest.mock import patch, MagicMock
from scripts.descobrir_edicao import buscar_edicoes_novas, ler_estado, salvar_estado
from pathlib import Path
import json
import tempfile
import os


def test_ler_estado_existente(tmp_path, monkeypatch):
    estado_file = tmp_path / "estado.json"
    estado_file.write_text('{"ultimo_id": 14419}', encoding="utf-8")
    monkeypatch.setattr("scripts.descobrir_edicao.ESTADO_PATH", estado_file)
    assert ler_estado() == {"ultimo_id": 14419}


def test_ler_estado_ausente(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "scripts.descobrir_edicao.ESTADO_PATH", tmp_path / "inexistente.json"
    )
    assert ler_estado() == {"ultimo_id": 14419}


def test_salvar_estado(tmp_path, monkeypatch):
    estado_file = tmp_path / "estado.json"
    monkeypatch.setattr("scripts.descobrir_edicao.ESTADO_PATH", estado_file)
    salvar_estado({"ultimo_id": 14420})
    assert json.loads(estado_file.read_text()) == {"ultimo_id": 14420}


def test_encontra_proxima_edicao():
    estado = {"ultimo_id": 14419}
    pdf_falso = b"%PDF-1.4 conteudo de teste"
    with patch("scripts.descobrir_edicao.requests.get") as mock_get:
        mock_get.side_effect = [
            MagicMock(status_code=200, content=pdf_falso),
            MagicMock(status_code=404, content=b""),
        ]
        resultado = buscar_edicoes_novas(estado)
    ids = [edicao_id for edicao_id, _ in resultado]
    assert ids == [14420]


def test_encontra_multiplas_edicoes():
    estado = {"ultimo_id": 14419}
    pdf_falso = b"%PDF-1.4 conteudo"
    with patch("scripts.descobrir_edicao.requests.get") as mock_get:
        mock_get.side_effect = [
            MagicMock(status_code=200, content=pdf_falso),
            MagicMock(status_code=200, content=pdf_falso),
            MagicMock(status_code=404, content=b""),
        ]
        resultado = buscar_edicoes_novas(estado)
    ids = [edicao_id for edicao_id, _ in resultado]
    assert ids == [14420, 14421]


def test_nenhuma_edicao_nova():
    estado = {"ultimo_id": 14419}
    with patch("scripts.descobrir_edicao.requests.get") as mock_get:
        mock_get.return_value = MagicMock(status_code=404, content=b"")
        resultado = buscar_edicoes_novas(estado)
    assert resultado == []


def test_ignora_resposta_sem_pdf():
    estado = {"ultimo_id": 14419}
    with patch("scripts.descobrir_edicao.requests.get") as mock_get:
        mock_get.return_value = MagicMock(status_code=200, content=b"<html>not a pdf</html>")
        resultado = buscar_edicoes_novas(estado)
    assert resultado == []
