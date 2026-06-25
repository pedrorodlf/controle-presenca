import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from src.controle_presenca.api.main import app
from src.controle_presenca.api.routes.alunos import get_db
from src.controle_presenca.database.models import Aluno

mock_db = MagicMock()

@pytest.fixture(autouse=True)
def setup_db():
    app.dependency_overrides[get_db] = lambda: mock_db
    yield
    app.dependency_overrides.clear()
    mock_db.reset_mock()

def test_listar_alunos():
    client = TestClient(app)
    aluno_mock = Aluno(id=1, cartao_id=123, nome="Teste", status="ATIVADO")
    mock_db.query.return_value.offset.return_value.limit.return_value.all.return_value = [aluno_mock]
    
    response = client.get("/alunos/")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["nome"] == "Teste"

def test_get_aluno_sucesso():
    client = TestClient(app)
    aluno_mock = Aluno(id=1, cartao_id=123, nome="Teste", status="ATIVADO")
    mock_db.query.return_value.filter.return_value.first.return_value = aluno_mock
    
    response = client.get("/alunos/1")
    assert response.status_code == 200
    assert response.json()["nome"] == "Teste"

def test_get_aluno_404():
    client = TestClient(app)
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    response = client.get("/alunos/999")
    assert response.status_code == 404

def test_criar_aluno_sucesso():
    client = TestClient(app)
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    def mock_refresh(obj):
        obj.id = 1
    mock_db.refresh.side_effect = mock_refresh
    
    response = client.post("/alunos/", json={"cartao_id": 123456, "nome": "Novo Aluno"})
    assert response.status_code == 201
    assert response.json()["nome"] == "Novo Aluno"

def test_criar_aluno_duplicado():
    client = TestClient(app)
    mock_db.query.return_value.filter.return_value.first.return_value = MagicMock()
    
    response = client.post("/alunos/", json={"cartao_id": 123456, "nome": "Novo Aluno"})
    assert response.status_code == 400

def test_desativar_aluno_sucesso():
    client = TestClient(app)
    aluno_mock = MagicMock()
    aluno_mock.status = "ATIVADO"
    mock_db.query.return_value.filter.return_value.first.return_value = aluno_mock
    
    response = client.delete("/alunos/1")
    assert response.status_code == 200
    assert aluno_mock.status == "DESATIVADO"

def test_desativar_aluno_nao_encontrado():
    client = TestClient(app)
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    response = client.delete("/alunos/999")
    assert response.status_code == 404

def test_desativar_aluno_ja_desativado():
    client = TestClient(app)
    aluno_mock = MagicMock()
    aluno_mock.status = "DESATIVADO"
    mock_db.query.return_value.filter.return_value.first.return_value = aluno_mock
    
    response = client.delete("/alunos/1")
    assert response.status_code == 400
