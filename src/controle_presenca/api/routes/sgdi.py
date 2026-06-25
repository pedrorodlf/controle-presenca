from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from typing import Dict, Annotated

from src.controle_presenca.database.connection import get_db
from src.controle_presenca.services.sgdi_service import SGDiService
from src.controle_presenca.services.google_sheets_service import GoogleSheetsService
from src.controle_presenca.services.cartola_magica_service import CartolaMagicaService

# ==========================================
# 1. Roteador exclusivo do SGDI
# ==========================================
router_sgdi = APIRouter(prefix="/sgdi", tags=["SGDI"])

@router_sgdi.post(
    "/sincronizar-forms",
    status_code=status.HTTP_200_OK,
    responses={
        404: {"description": "Planilha ou credenciais não encontradas"},
        400: {"description": "Dados da planilha inválidos"},
        500: {"description": "Erro interno no servidor"}
    }
)
def sincronizar_forms(db: Annotated[Session, Depends(get_db)]):
    """Busca todas as respostas direto na planilha do Google Forms usando a URL do .env."""
    service = GoogleSheetsService(db)
    try:
        resultado = service.sincronizar_dados_forms()
        return {
            "mensagem": "Sincronização com o Google concluída!",
            "detalhes": resultado,
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro interno: {str(e)}")

class RegistroCandidatoRequest(BaseModel):
    nome: str
    cpf: str
    email: EmailStr
    respostas_questionario: Dict[str, str]

@router_sgdi.post(
    "/candidatos",
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"description": "Dados do candidato inválidos"},
        500: {"description": "Erro interno no servidor"}
    }
)
def inscrever_candidato(payload: RegistroCandidatoRequest, db: Annotated[Session, Depends(get_db)]):
    """Endpoint para receber os dados de um candidato manualmente e registrá-lo."""
    service = SGDiService(db)
    try:
        candidato = service.registrar_novo_candidato(
            nome=payload.nome,
            cpf=payload.cpf,
            email=payload.email,
            respostas_questionario=payload.respostas_questionario,
        )
        return {
            "mensagem": "Candidato registrado com sucesso!",
            "dados": {
                "id": candidato.id,
                "nome": candidato.nome,
                "pontuacao": candidato.pontuacao_socioeconomica,
            },
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno no servidor.")

@router_sgdi.get(
    "/candidatos/busca",
    status_code=status.HTTP_200_OK,
    responses={
        404: {"description": "Nenhum candidato encontrado"}
    }
)
def buscar_candidato(termo: str, db: Annotated[Session, Depends(get_db)]):
    """Pesquisa candidatos por CPF exato ou parte do nome."""
    service = SGDiService(db)
    resultados = service.buscar_candidato_por_cpf_ou_nome(termo)
    if not resultados:
        raise HTTPException(status_code=404, detail="Nenhum candidato encontrado com esse termo.")
    return {"resultados": resultados}

@router_sgdi.delete(
    "/candidatos/{cpf}",
    status_code=status.HTTP_200_OK,
    responses={
        404: {"description": "Candidato não encontrado"},
        500: {"description": "Erro ao remover candidato"}
    }
)
def remover_candidato(cpf: str, db: Annotated[Session, Depends(get_db)]):
    """Remove um candidato do sistema pelo CPF."""
    service = SGDiService(db)
    try:
        service.remover_candidato(cpf)
        return {"mensagem": f"Candidato com CPF {cpf} removido com sucesso."}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao remover: {str(e)}")

@router_sgdi.post("/fechar-turma", status_code=status.HTTP_200_OK)
def fechar_turma_e_aprovar(db: Annotated[Session, Depends(get_db)], vagas: int = 60):
    """Roda o algoritmo de corte e aprova estritamente o número de vagas estipulado."""
    service = SGDiService(db)
    qtd_aprovados = service.aprovar_turma_oficial(limite_vagas=vagas)
    return {
        "mensagem": "Processo de seleção finalizado!",
        "vagas_preenchidas": qtd_aprovados,
    }

@router_sgdi.post(
    "/candidatos/{cpf}/matricular",
    status_code=status.HTTP_200_OK,
    responses={
        400: {"description": "Erro ao matricular candidato"},
        404: {"description": "Candidato não encontrado"},
        500: {"description": "Erro interno no servidor"}
    }
)
def matricular_candidato(cpf: str, background_tasks: BackgroundTasks, db: Annotated[Session, Depends(get_db)]):
    """Efetiva a matrícula e agenda o e-mail para o segundo plano."""
    service = SGDiService(db)
    try:
        sucesso, mensagem = service.matricular_candidato(cpf, background_tasks=background_tasks)
        if not sucesso:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=mensagem)
        return {
            "status": "sucesso", 
            "mensagem": "Matrícula efetuada! O e-mail com o cartão está a ser enviado em segundo plano."
        }
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Erro interno no servidor.")

# ---> ROTA DE RANKING ADICIONADA AQUI <---
@router_sgdi.get("/ranking", status_code=status.HTTP_200_OK)
def obter_ranking(db: Annotated[Session, Depends(get_db)]):
    """Retorna a lista de candidatos pendentes e aprovados para a tabela do painel."""
    service = SGDiService(db)
    candidatos = service.gerar_ranking(limite=100)
    
    # TRADUÇÃO: Converte explicitamente para dicionário para evitar erro 500 do FastAPI
    return [
        {
            "id": c.id,
            "nome": c.nome,
            "cpf": c.cpf,
            "pontuacao_socioeconomica": c.pontuacao_socioeconomica,
            "status": c.status
        }
        for c in candidatos
    ]

# ==========================================
# 2. Roteador exclusivo dos Relatórios
# ==========================================
router_relatorios = APIRouter(prefix="/relatorios", tags=["Relatórios (Cartola Mágica)"])

@router_relatorios.get("/frequencia", status_code=status.HTTP_200_OK)
def obter_frequencia_geral(db: Annotated[Session, Depends(get_db)]):
    """Gera o relatório completo de presenças e faltas da turma."""
    try:
        service = CartolaMagicaService(db)
        return service.gerar_relatorio_frequencia()
    except Exception:
        # PROTEÇÃO: Se a tabela estiver vazia ou o serviço quebrar, devolve JSON limpo
        return {"total_sessoes_gerais": 0, "alunos": []}
