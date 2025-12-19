"""Rotas da API para endpoints de Fazenda."""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import DatabaseException, FazendaNotFoundException
from app.fazendas.repositories.fazenda_repository import FazendaRepository
from app.fazendas.schemas import (
    BuscaPontoRequest,
    BuscaRaioRequest,
    BuscaRaioResponse,
    FazendaSchema,
)
from app.fazendas.services.fazenda_service import FazendaService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/{gid}",
    response_model=FazendaSchema,
    summary="Buscar fazenda por ID",
    description="Retorna os dados de uma fazenda específica pelo seu GID",
    responses={
        200: {"description": "Fazenda encontrada com sucesso"},
        404: {"description": "Fazenda não encontrada"},
        500: {"description": "Erro interno do servidor"},
    },
)
def get_fazenda(gid: int, db: Session = Depends(get_db)):
    """Busca fazenda por GID."""
    try:
        logger.info(f"Buscando fazenda com GID: {gid}")

        repository = FazendaRepository(db)
        fazenda = repository.get_by_id(gid)

        if not fazenda:
            logger.warning(f"Fazenda com GID {gid} não encontrada")
            raise FazendaNotFoundException(gid)

        logger.info(
            f"Fazenda {gid} encontrada: {fazenda.municipio}/{fazenda.cod_estado}"
        )
        return FazendaService.serialize_fazenda(fazenda)

    except FazendaNotFoundException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Erro de banco de dados ao buscar fazenda {gid}: {str(e)}")
        raise DatabaseException("Erro ao buscar fazenda no banco de dados")
    except Exception as e:
        logger.error(f"Erro inesperado ao buscar fazenda {gid}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.post(
    "/busca-ponto",
    response_model=List[FazendaSchema],
    summary="Buscar fazendas por ponto",
    description="Retorna todas as fazendas que contêm o ponto especificado (latitude/longitude)",
    responses={
        200: {"description": "Busca realizada com sucesso"},
        400: {"description": "Coordenadas inválidas"},
        500: {"description": "Erro interno do servidor"},
    },
)
def busca_ponto(request: BuscaPontoRequest, db: Session = Depends(get_db)):
    """Busca fazendas que contêm um ponto específico."""
    try:
        logger.info(
            f"Buscando fazendas no ponto: ({request.latitude}, {request.longitude})"
        )

        repository = FazendaRepository(db)
        fazendas = repository.find_by_point(request.latitude, request.longitude)

        logger.info(f"Encontradas {len(fazendas)} fazendas no ponto especificado")
        return [FazendaService.serialize_fazenda(f) for f in fazendas]

    except SQLAlchemyError as e:
        logger.error(f"Erro de banco de dados na busca por ponto: {str(e)}")
        raise DatabaseException("Erro ao buscar fazendas no banco de dados")
    except Exception as e:
        logger.error(f"Erro inesperado na busca por ponto: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.post(
    "/busca-raio",
    response_model=BuscaRaioResponse,
    summary="Buscar fazendas por raio",
    description="Retorna todas as fazendas dentro de um raio (em km) a partir de um ponto central, com paginação",
    responses={
        200: {"description": "Busca realizada com sucesso"},
        400: {"description": "Parâmetros inválidos"},
        500: {"description": "Erro interno do servidor"},
    },
)
def busca_raio(request: BuscaRaioRequest, db: Session = Depends(get_db)):
    """Busca fazendas dentro de um raio a partir de um ponto com paginação."""
    try:
        logger.info(
            f"Buscando fazendas em raio de {request.raio_km}km do ponto: "
            f"({request.latitude}, {request.longitude}) - Página {request.page}, Tamanho {request.page_size}"
        )

        # Calcula paginação
        offset, _ = FazendaService.calculate_pagination(
            0, request.page, request.page_size
        )

        # Obtém fazendas do repositório
        repository = FazendaRepository(db)
        fazendas, total_count = repository.find_by_radius(
            request.latitude,
            request.longitude,
            request.raio_km,
            offset,
            request.page_size,
        )

        # Recalcula total de páginas com a contagem real
        _, total_pages = FazendaService.calculate_pagination(
            total_count, request.page, request.page_size
        )

        logger.info(
            f"Encontradas {total_count} fazendas no total, "
            f"retornando {len(fazendas)} na página {request.page}/{total_pages}"
        )

        return BuscaRaioResponse(
            count=total_count,
            page=request.page,
            page_size=request.page_size,
            total_pages=total_pages,
            raio_km=request.raio_km,
            results=[FazendaService.serialize_fazenda(f) for f in fazendas],
        )

    except SQLAlchemyError as e:
        logger.error(f"Erro de banco de dados na busca por raio: {str(e)}")
        raise DatabaseException("Erro ao buscar fazendas no banco de dados")
    except Exception as e:
        logger.error(f"Erro inesperado na busca por raio: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")
