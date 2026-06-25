import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from datetime import datetime
from src.controle_presenca.api.main import app

def test_sessao_ativa_404():
    client = TestClient(app)
    with patch('src.controle_presenca.api.routes.sessao.RepositoriosPresenca') as MockRepo:
        mock_repo = MagicMock()
        MockRepo.return_value = mock_repo
        mock_repo.obter_sessao_ativa.return_value = None
        
        response = client.get("/sessao/ativa")
        assert response.status_code == 404

def test_sessao_ativa_200():
    client = TestClient(app)
    with patch('src.controle_presenca.api.routes.sessao.RepositoriosPresenca') as MockRepo:
        mock_repo = MagicMock()
        MockRepo.return_value = mock_repo
        
        mock_sessao = MagicMock()
        mock_sessao.id = 1
        mock_sessao.inicio = datetime(2026, 1, 1, 10, 0, 0)
        mock_sessao.status = "ativa"
        mock_repo.obter_sessao_ativa.return_value = mock_sessao
        
        response = client.get("/sessao/ativa")
        assert response.status_code == 200
        assert response.json()["id"] == 1

def test_iniciar_sessao():
    client = TestClient(app)
    with patch('src.controle_presenca.api.routes.sessao.RepositoriosPresenca') as MockRepo:
        mock_repo = MagicMock()
        MockRepo.return_value = mock_repo
        mock_repo.obter_sessao_ativa.return_value = None
        
        mock_sessao = MagicMock()
        mock_sessao.id = 1
        mock_sessao.inicio = datetime.now()
        mock_sessao.status = "ativa"
        mock_repo.criar_sessao.return_value = mock_sessao
        
        response = client.post("/sessao/iniciar")
        assert response.status_code == 200
        assert response.json()["status"] == "ativa"

def test_iniciar_sessao_ja_ativa():
    client = TestClient(app)
    with patch('src.controle_presenca.api.routes.sessao.RepositoriosPresenca') as MockRepo:
        mock_repo = MagicMock()
        MockRepo.return_value = mock_repo
        mock_repo.obter_sessao_ativa.return_value = MagicMock()
        
        response = client.post("/sessao/iniciar")
        assert response.status_code == 400

def test_encerrar_sessao_sucesso():
    client = TestClient(app)
    with patch('src.controle_presenca.api.routes.sessao.RepositoriosPresenca') as MockRepo:
        mock_repo = MagicMock()
        MockRepo.return_value = mock_repo
        
        mock_sessao = MagicMock()
        mock_sessao.id = 1
        mock_repo.obter_sessao_ativa.return_value = mock_sessao
        
        response = client.post("/sessao/encerrar")
        assert response.status_code == 200
        assert response.json()["sucesso"] is True

def test_encerrar_sessao_sem_sessao():
    client = TestClient(app)
    with patch('src.controle_presenca.api.routes.sessao.RepositoriosPresenca') as MockRepo:
        mock_repo = MagicMock()
        MockRepo.return_value = mock_repo
        mock_repo.obter_sessao_ativa.return_value = None
        
        response = client.post("/sessao/encerrar")
        assert response.status_code == 404
