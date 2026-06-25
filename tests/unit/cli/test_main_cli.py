import pytest
import sys
sys.path.insert(0, '/app/src')

from unittest.mock import patch, MagicMock

def test_main_import():
    """Testa se main.py pode ser importado"""
    import controle_presenca.main
    assert controle_presenca.main is not None

def test_main_has_menu_functions():
    """Testa se main.py tem as funções de menu"""
    from controle_presenca.main import iniciar_sessao_aula, encerrar_sessao_aula, limpar_tela, _pausar
    
    assert callable(iniciar_sessao_aula)
    assert callable(encerrar_sessao_aula)
    assert callable(limpar_tela)
    assert callable(_pausar)

def test_limpar_tela_execution():
    """Testa se limpar_tela executa sem erro"""
    from controle_presenca.main import limpar_tela
    
    with patch('os.system') as mock_system:
        limpar_tela()
        mock_system.assert_called_once_with('clear')

def test_pausar_execution():
    """Testa se _pausar aguarda input"""
    from controle_presenca.main import _pausar
    
    with patch('builtins.input') as mock_input:
        _pausar()
        mock_input.assert_called_once()

def test_iniciar_sessao_aula_sem_sessao_ativa():
    """Testa iniciar sessão quando não há sessão ativa"""
    from controle_presenca.main import iniciar_sessao_aula
    
    with patch('controle_presenca.main.SessionLocal') as MockSessionLocal:
        mock_db = MagicMock()
        MockSessionLocal.return_value.__enter__.return_value = mock_db
        
        mock_repo = MagicMock()
        mock_repo.obter_sessao_ativa.return_value = None
        mock_repo.criar_sessao.return_value = True
        
        with patch('controle_presenca.main.PresencaService') as MockService:
            MockService.return_value.repo = mock_repo
            
            with patch('builtins.input') as mock_input:
                iniciar_sessao_aula()
                
                mock_repo.obter_sessao_ativa.assert_called_once()
                mock_repo.criar_sessao.assert_called_once()

def test_iniciar_sessao_aula_com_sessao_ativa():
    """Testa iniciar sessão quando já existe sessão ativa"""
    from controle_presenca.main import iniciar_sessao_aula
    
    with patch('controle_presenca.main.SessionLocal') as MockSessionLocal:
        mock_db = MagicMock()
        MockSessionLocal.return_value.__enter__.return_value = mock_db
        
        mock_repo = MagicMock()
        mock_repo.obter_sessao_ativa.return_value = MagicMock()  # Sessão existe
        
        with patch('controle_presenca.main.PresencaService') as MockService:
            MockService.return_value.repo = mock_repo
            
            with patch('builtins.input') as mock_input:
                with patch('builtins.print') as mock_print:
                    iniciar_sessao_aula()
                    
                    mock_repo.obter_sessao_ativa.assert_called_once()
                    mock_repo.criar_sessao.assert_not_called()
                    # Verifica se a mensagem de aviso foi impressa
                    mock_print.assert_any_call("\n⚠️ Sessão já ativa!")

def test_encerrar_sessao_aula():
    """Testa encerrar sessão de aula"""
    from controle_presenca.main import encerrar_sessao_aula
    
    with patch('controle_presenca.main.SessionLocal') as MockSessionLocal:
        mock_db = MagicMock()
        MockSessionLocal.return_value.__enter__.return_value = mock_db
        
        mock_repo = MagicMock()
        mock_repo.encerrar_sessao.return_value = True
        
        with patch('controle_presenca.main.PresencaService') as MockService:
            MockService.return_value.repo = mock_repo
            
            with patch('builtins.input') as mock_input:
                with patch('builtins.print') as mock_print:
                    encerrar_sessao_aula()
                    
                    mock_repo.encerrar_sessao.assert_called_once()
                    mock_print.assert_any_call("\n✅ Sessão encerrada!")

def test_encerrar_sessao_aula_sem_sessao():
    """Testa encerrar sessão de aula quando não há sessão ativa"""
    from controle_presenca.main import encerrar_sessao_aula
    
    with patch('controle_presenca.main.SessionLocal') as MockSessionLocal:
        mock_db = MagicMock()
        MockSessionLocal.return_value.__enter__.return_value = mock_db
        
        mock_repo = MagicMock()
        mock_repo.obter_sessao_ativa.return_value = None
        
        with patch('controle_presenca.main.PresencaService') as MockService:
            MockService.return_value.repo = mock_repo
            
            with patch('builtins.input') as mock_input, \
                 patch('builtins.print') as mock_print:
                encerrar_sessao_aula()
                mock_print.assert_any_call("\n⚠️ Nenhuma sessão ativa.")

def test_bater_ponto_sem_sessao():
    from controle_presenca.main import bater_ponto
    with patch('controle_presenca.main.SessionLocal') as MockSessionLocal:
        mock_db = MagicMock()
        MockSessionLocal.return_value.__enter__.return_value = mock_db
        mock_repo = MagicMock()
        mock_repo.obter_sessao_ativa.return_value = None
        
        with patch('controle_presenca.main.PresencaService') as MockService:
            MockService.return_value.repo = mock_repo
            
            with patch('builtins.print') as mock_print, \
                 patch('controle_presenca.main._pausar') as mock_pausar:
                bater_ponto()
                mock_print.assert_any_call("\n⚠️ Inicie a sessão primeiro!")

def test_bater_ponto_com_sessao_e_sair():
    from controle_presenca.main import bater_ponto
    with patch('controle_presenca.main.SessionLocal') as MockSessionLocal:
        mock_db = MagicMock()
        MockSessionLocal.return_value.__enter__.return_value = mock_db
        mock_repo = MagicMock()
        mock_repo.obter_sessao_ativa.return_value = MagicMock()
        
        with patch('controle_presenca.main.PresencaService') as MockService:
            MockService.return_value.repo = mock_repo
            MockService.return_value.processar_leitura.return_value = (True, "Sucesso")
            
            with patch('builtins.input', side_effect=['123', 'sair']) as mock_input, \
                 patch('builtins.print') as mock_print:
                bater_ponto()
                mock_print.assert_any_call("✅ Sucesso")

def test_exibir_ranking_sgdi():
    from controle_presenca.main import exibir_ranking_sgdi
    with patch('controle_presenca.main.SessionLocal') as MockSessionLocal:
        mock_db = MagicMock()
        MockSessionLocal.return_value.__enter__.return_value = mock_db
        
        mock_cand = MagicMock()
        mock_cand.nome = "Teste"
        mock_cand.cpf = "123"
        mock_cand.pontuacao_socioeconomica = 10.0
        
        with patch('controle_presenca.main.SGDiService') as MockService:
            MockService.return_value.gerar_ranking.return_value = [mock_cand]
            
            with patch('builtins.print') as mock_print, \
                 patch('controle_presenca.main._pausar') as mock_pausar:
                exibir_ranking_sgdi()
                mock_print.assert_any_call("1º | Teste | CPF: 123 | Pontos: 10.0")

def test_aprovar_candidatos_sgdi():
    from controle_presenca.main import aprovar_candidatos_sgdi
    with patch('controle_presenca.main.SessionLocal') as MockSessionLocal:
        mock_db = MagicMock()
        MockSessionLocal.return_value.__enter__.return_value = mock_db
        
        with patch('controle_presenca.main.SGDiService') as MockService:
            MockService.return_value.aprovar_corte.return_value = 5
            
            with patch('builtins.input', side_effect=['5']) as mock_input, \
                 patch('builtins.print') as mock_print, \
                 patch('controle_presenca.main._pausar') as mock_pausar:
                aprovar_candidatos_sgdi()
                mock_print.assert_any_call("\n✅ 5 candidatos aprovados com sucesso!")

def test_efetivar_matricula_sgdi():
    from controle_presenca.main import efetivar_matricula_sgdi
    with patch('controle_presenca.main.SessionLocal') as MockSessionLocal:
        mock_db = MagicMock()
        MockSessionLocal.return_value.__enter__.return_value = mock_db
        
        with patch('controle_presenca.main.SGDiService') as MockService:
            MockService.return_value.matricular_candidato.return_value = (True, "Sucesso")
            
            with patch('builtins.input', side_effect=['12345678901']) as mock_input, \
                 patch('builtins.print') as mock_print, \
                 patch('controle_presenca.main._pausar') as mock_pausar:
                efetivar_matricula_sgdi()
                mock_print.assert_any_call("\nSucesso")

def test_executar_menu_exit():
    from controle_presenca.main import executar_menu
    with patch('builtins.input', side_effect=['3']) as mock_input, \
         patch('builtins.print') as mock_print:
        executar_menu()
        mock_print.assert_any_call("\n👋 Encerrando o sistema...")

def test_executar_menu_invalid_then_exit():
    from controle_presenca.main import executar_menu
    with patch('builtins.input', side_effect=['9', '', '3']) as mock_input, \
         patch('builtins.print') as mock_print:
        executar_menu()
        mock_print.assert_any_call("\n❌ Opção inválida!")

def test_executar_menu_leitor_then_exit():
    from controle_presenca.main import executar_menu
    with patch('builtins.input', side_effect=['1', '4', '3']) as mock_input:
        executar_menu()

def test_executar_menu_sgdi_then_exit():
    from controle_presenca.main import executar_menu
    with patch('builtins.input', side_effect=['2', '4', '3']) as mock_input:
        executar_menu()
