import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from src.controle_presenca.api.main import app
from src.controle_presenca.database.models import Candidato

def test_sincronizar_forms_sucesso():
    client = TestClient(app)
    with patch('src.controle_presenca.api.routes.sgdi.GoogleSheetsService') as MockService:
        mock_service = MagicMock()
        MockService.return_value = mock_service
        mock_service.sincronizar_dados_forms.return_value = "OK"
        
        response = client.post("/sgdi/sincronizar-forms")
        assert response.status_code == 200
        assert "concluída" in response.json()["mensagem"].lower()

def test_sincronizar_forms_erro_value():
    client = TestClient(app)
    with patch('src.controle_presenca.api.routes.sgdi.GoogleSheetsService') as MockService:
        mock_service = MagicMock()
        MockService.return_value = mock_service
        mock_service.sincronizar_dados_forms.side_effect = ValueError("Erro de valor")
        
        response = client.post("/sgdi/sincronizar-forms")
        assert response.status_code == 400

def test_inscrever_candidato_sucesso():
    client = TestClient(app)
    with patch('src.controle_presenca.api.routes.sgdi.SGDiService') as MockService:
        mock_service = MagicMock()
        MockService.return_value = mock_service
        
        mock_cand = MagicMock()
        mock_cand.id = 1
        mock_cand.nome = "Teste"
        mock_cand.pontuacao_socioeconomica = 10.0
        mock_service.registrar_novo_candidato.return_value = mock_cand
        
        payload = {
            "nome": "Teste",
            "cpf": "123",
            "email": "test@test.com",
            "respostas_questionario": {}
        }
        response = client.post("/sgdi/candidatos", json=payload)
        assert response.status_code == 201
        assert response.json()["dados"]["nome"] == "Teste"

def test_buscar_candidato_sucesso():
    client = TestClient(app)
    with patch('src.controle_presenca.api.routes.sgdi.SGDiService') as MockService:
        mock_service = MagicMock()
        MockService.return_value = mock_service
        mock_service.buscar_candidato_por_cpf_ou_nome.return_value = [{"nome": "Candidato"}]
        
        response = client.get("/sgdi/candidatos/busca?termo=teste")
        assert response.status_code == 200
        assert len(response.json()["resultados"]) == 1

def test_buscar_candidato_404():
    client = TestClient(app)
    with patch('src.controle_presenca.api.routes.sgdi.SGDiService') as MockService:
        mock_service = MagicMock()
        MockService.return_value = mock_service
        mock_service.buscar_candidato_por_cpf_ou_nome.return_value = []
        
        response = client.get("/sgdi/candidatos/busca?termo=teste")
        assert response.status_code == 404

def test_remover_candidato_sucesso():
    client = TestClient(app)
    with patch('src.controle_presenca.api.routes.sgdi.SGDiService') as MockService:
        mock_service = MagicMock()
        MockService.return_value = mock_service
        
        response = client.delete("/sgdi/candidatos/12345678901")
        assert response.status_code == 200

def test_remover_candidato_erro():
    client = TestClient(app)
    with patch('src.controle_presenca.api.routes.sgdi.SGDiService') as MockService:
        mock_service = MagicMock()
        MockService.return_value = mock_service
        mock_service.remover_candidato.side_effect = ValueError("Erro")
        
        response = client.delete("/sgdi/candidatos/12345678901")
        assert response.status_code == 404

def test_fechar_turma_sucesso():
    client = TestClient(app)
    with patch('src.controle_presenca.api.routes.sgdi.SGDiService') as MockService:
        mock_service = MagicMock()
        MockService.return_value = mock_service
        mock_service.aprovar_turma_oficial.return_value = 50
        
        response = client.post("/sgdi/fechar-turma?vagas=50")
        assert response.status_code == 200
        assert response.json()["vagas_preenchidas"] == 50

def test_matricular_candidato_sucesso():
    client = TestClient(app)
    with patch('src.controle_presenca.api.routes.sgdi.SGDiService') as MockService:
        mock_service = MagicMock()
        MockService.return_value = mock_service
        mock_service.matricular_candidato.return_value = (True, "Sucesso")
        
        response = client.post("/sgdi/candidatos/123/matricular")
        assert response.status_code == 200

def test_matricular_candidato_erro():
    client = TestClient(app)
    with patch('src.controle_presenca.api.routes.sgdi.SGDiService') as MockService:
        mock_service = MagicMock()
        MockService.return_value = mock_service
        mock_service.matricular_candidato.return_value = (False, "Erro")
        
        response = client.post("/sgdi/candidatos/123/matricular")
        assert response.status_code == 400

def test_obter_ranking():
    client = TestClient(app)
    with patch('src.controle_presenca.api.routes.sgdi.SGDiService') as MockService:
        mock_service = MagicMock()
        MockService.return_value = mock_service
        
        cand = Candidato(id=1, nome="C1", cpf="123", status="pendente", pontuacao_socioeconomica=10.0)
        mock_service.gerar_ranking.return_value = [cand]
        
        response = client.get("/sgdi/ranking")
        assert response.status_code == 200
        assert len(response.json()) == 1

def test_obter_frequencia_geral():
    client = TestClient(app)
    with patch('src.controle_presenca.api.routes.sgdi.CartolaMagicaService') as MockService:
        mock_service = MagicMock()
        MockService.return_value = mock_service
        mock_service.gerar_relatorio_frequencia.return_value = {"total": 10}
        
        response = client.get("/relatorios/frequencia")
        assert response.status_code == 200
        assert response.json()["total"] == 10
