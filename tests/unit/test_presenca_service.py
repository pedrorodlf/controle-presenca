import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone

# Importar o serviço
try:
    from controle_presenca.services.presenca_service import PresencaService
except ImportError:
    pytest.skip("PresencaService não disponível", allow_module_level=True)

class TestPresencaService:
    
    def test_processar_leitura_sem_sessao_ativa(self):
        """Testa batida de ponto quando não há sessão ativa"""
        mock_db = MagicMock()
        service = PresencaService(mock_db)
        service.repo = MagicMock()
        service.repo.obter_sessao_ativa.return_value = None
        
        sucesso, mensagem = service.processar_leitura("123456")
        
        assert sucesso is False
        assert "aula ativa" in mensagem.lower() or "nenhuma aula ativa" in mensagem.lower()
    
    def test_processar_leitura_com_sessao_ativa_e_cartao_valido(self):
        """Testa batida de ponto com sessão ativa e cartão válido"""
        mock_db = MagicMock()
        service = PresencaService(mock_db)
        service.repo = MagicMock()
        
        # Simula uma sessão ativa
        sessao_mock = MagicMock()
        sessao_mock.id = 1
        service.repo.obter_sessao_ativa.return_value = sessao_mock
        
        # Simula que o aluno existe e está ativo
        aluno_mock = MagicMock()
        aluno_mock.id = 1
        aluno_mock.nome = "Aluno Teste"
        aluno_mock.status = "ATIVADO"
        service.repo.buscar_aluno.return_value = aluno_mock
        
        # Simula que não há registro anterior (primeira entrada)
        service.repo.obter_ultimo_registro.return_value = None
        
        # Simula que registro de ponto é salvo
        service.repo.registrar_ponto.return_value = True
        
        sucesso, mensagem = service.processar_leitura("123456")
        
        # Verificações
        assert sucesso is True
        assert "entrada" in mensagem.lower()
        assert "aluno teste" in mensagem.lower()
        
        # Verifica se o método correto foi chamado com os parâmetros certos
        service.repo.registrar_ponto.assert_called_once_with(1, 1, 'entrada')
    
    def test_processar_leitura_com_saida(self):
        """Testa batida de ponto para saída (quando já tem entrada registrada)"""
        mock_db = MagicMock()
        service = PresencaService(mock_db)
        service.repo = MagicMock()
        
        # Simula uma sessão ativa
        sessao_mock = MagicMock()
        sessao_mock.id = 1
        service.repo.obter_sessao_ativa.return_value = sessao_mock
        
        # Simula que o aluno existe e está ativo
        aluno_mock = MagicMock()
        aluno_mock.id = 1
        aluno_mock.nome = "Aluno Teste"
        aluno_mock.status = "ATIVADO"
        service.repo.buscar_aluno.return_value = aluno_mock
        
        # Simula que já tem um registro de entrada
        ultimo_registro = MagicMock()
        ultimo_registro.tipo = 'entrada'
        service.repo.obter_ultimo_registro.return_value = ultimo_registro
        
        sucesso, mensagem = service.processar_leitura("123456")
        
        # Verificações
        assert sucesso is True
        assert "saída" in mensagem.lower()
        service.repo.registrar_ponto.assert_called_once_with(1, 1, 'saida')
    
    def test_processar_leitura_com_cartao_invalido(self):
        """Testa batida de ponto com cartão não numérico"""
        mock_db = MagicMock()
        service = PresencaService(mock_db)
        service.repo = MagicMock()
        
        # Sessão ativa existe
        sessao_mock = MagicMock()
        sessao_mock.id = 1
        service.repo.obter_sessao_ativa.return_value = sessao_mock
        
        sucesso, mensagem = service.processar_leitura("ABC123")
        
        assert sucesso is False
        assert "numérico" in mensagem.lower()
    
    def test_processar_leitura_com_cartao_nao_cadastrado(self):
        """Testa batida de ponto com cartão não cadastrado"""
        mock_db = MagicMock()
        service = PresencaService(mock_db)
        service.repo = MagicMock()
        
        # Sessão ativa existe
        sessao_mock = MagicMock()
        sessao_mock.id = 1
        service.repo.obter_sessao_ativa.return_value = sessao_mock
        
        # Aluno não encontrado
        service.repo.buscar_aluno.return_value = None
        
        sucesso, mensagem = service.processar_leitura("123456")
        
        assert sucesso is False
        assert "não cadastrado" in mensagem.lower()
    
    def test_processar_leitura_com_aluno_inativo(self):
        """Testa batida de ponto com aluno inativo"""
        mock_db = MagicMock()
        service = PresencaService(mock_db)
        service.repo = MagicMock()
        
        # Sessão ativa existe
        sessao_mock = MagicMock()
        sessao_mock.id = 1
        service.repo.obter_sessao_ativa.return_value = sessao_mock
        
        # Aluno existe mas está inativo
        aluno_mock = MagicMock()
        aluno_mock.id = 1
        aluno_mock.nome = "Aluno Inativo"
        aluno_mock.status = "INATIVO"
        service.repo.buscar_aluno.return_value = aluno_mock
        
        sucesso, mensagem = service.processar_leitura("123456")
        
        assert sucesso is False
        assert "inativo" in mensagem.lower()

    def test_iniciar_sessao_sucesso(self):
        mock_db = MagicMock()
        service = PresencaService(mock_db)
        service.repo = MagicMock()
        service.repo.obter_sessao_ativa.return_value = None
        
        sucesso, msg = service.iniciar_sessao()
        assert sucesso is True
        assert "iniciada" in msg
        service.repo.criar_sessao.assert_called_once()

    def test_iniciar_sessao_ja_ativa(self):
        mock_db = MagicMock()
        service = PresencaService(mock_db)
        service.repo = MagicMock()
        service.repo.obter_sessao_ativa.return_value = MagicMock()
        
        sucesso, msg = service.iniciar_sessao()
        assert sucesso is False
        assert "já ativa" in msg

    def test_encerrar_sessao_sem_sessao(self):
        mock_db = MagicMock()
        service = PresencaService(mock_db)
        service.repo = MagicMock()
        service.repo.obter_sessao_ativa.return_value = None
        
        sucesso, msg = service.encerrar_sessao()
        assert sucesso is False
        assert "Nenhuma sessão ativa" in msg

    def test_encerrar_sessao_sucesso(self):
        mock_db = MagicMock()
        service = PresencaService(mock_db)
        service.repo = MagicMock()
        
        sessao_mock = MagicMock()
        sessao_mock.id = 1
        sessao_mock.inicio = datetime(2026, 1, 1, 10, 0, 0)
        sessao_mock.fim = datetime(2026, 1, 1, 12, 0, 0)
        service.repo.obter_sessao_ativa.return_value = sessao_mock
        
        # mock obter_intervalos_sessao
        service.repo.obter_intervalos_sessao.return_value = []
        
        # mock obter_alunos_ativos
        aluno_mock = MagicMock()
        aluno_mock.id = 1
        aluno_mock.carga_horaria_total = 10.0
        aluno_mock.percentual_presenca = 80.0
        service.repo.obter_alunos_ativos.return_value = [aluno_mock]
        
        # mock registros for calcular_tempo_presente_aluno
        reg_entrada = MagicMock()
        reg_entrada.tipo = 'entrada'
        reg_entrada.timestamp = datetime(2026, 1, 1, 10, 5, 0)
        reg_saida = MagicMock()
        reg_saida.tipo = 'saida'
        reg_saida.timestamp = datetime(2026, 1, 1, 11, 5, 0)
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [reg_entrada, reg_saida]
        
        sucesso, msg = service.encerrar_sessao()
        assert sucesso is True
        assert "encerrada" in msg
        assert aluno_mock.carga_horaria_total > 10.0

    def test_iniciar_intervalo_sucesso(self):
        mock_db = MagicMock()
        service = PresencaService(mock_db)
        service.repo = MagicMock()
        sessao_mock = MagicMock()
        sessao_mock.id = 1
        service.repo.obter_sessao_ativa.return_value = sessao_mock
        service.repo.obter_intervalo_ativo.return_value = None
        
        sucesso, msg = service.iniciar_intervalo()
        assert sucesso is True
        service.repo.iniciar_intervalo.assert_called_once_with(1)

    def test_iniciar_intervalo_sem_sessao(self):
        mock_db = MagicMock()
        service = PresencaService(mock_db)
        service.repo = MagicMock()
        service.repo.obter_sessao_ativa.return_value = None
        
        sucesso, msg = service.iniciar_intervalo()
        assert sucesso is False

    def test_iniciar_intervalo_ja_ativo(self):
        mock_db = MagicMock()
        service = PresencaService(mock_db)
        service.repo = MagicMock()
        sessao_mock = MagicMock()
        sessao_mock.id = 1
        service.repo.obter_sessao_ativa.return_value = sessao_mock
        service.repo.obter_intervalo_ativo.return_value = MagicMock()
        
        sucesso, msg = service.iniciar_intervalo()
        assert sucesso is False

    def test_encerrar_intervalo_sucesso(self):
        mock_db = MagicMock()
        service = PresencaService(mock_db)
        service.repo = MagicMock()
        sessao_mock = MagicMock()
        sessao_mock.id = 1
        service.repo.obter_sessao_ativa.return_value = sessao_mock
        service.repo.obter_intervalo_ativo.return_value = MagicMock()
        
        sucesso, msg = service.encerrar_intervalo()
        assert sucesso is True
        service.repo.encerrar_intervalo.assert_called_once_with(1)

    def test_encerrar_intervalo_sem_sessao(self):
        mock_db = MagicMock()
        service = PresencaService(mock_db)
        service.repo = MagicMock()
        service.repo.obter_sessao_ativa.return_value = None
        
        sucesso, msg = service.encerrar_intervalo()
        assert sucesso is False

    def test_encerrar_intervalo_sem_intervalo_ativo(self):
        mock_db = MagicMock()
        service = PresencaService(mock_db)
        service.repo = MagicMock()
        sessao_mock = MagicMock()
        sessao_mock.id = 1
        service.repo.obter_sessao_ativa.return_value = sessao_mock
        service.repo.obter_intervalo_ativo.return_value = None
        
        sucesso, msg = service.encerrar_intervalo()
        assert sucesso is False

    def test_diferenca_efetiva_com_timezone(self):
        mock_db = MagicMock()
        service = PresencaService(mock_db)
        t1 = datetime(2026, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        t2 = datetime(2026, 1, 1, 11, 0, 0, tzinfo=timezone.utc)
        res = service.diferenca_efetiva(t1, t2, [])
        assert res == 3600
