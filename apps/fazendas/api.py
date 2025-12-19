import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from geoalchemy2 import Geography
from geoalchemy2.shape import to_shape
from sqlalchemy import cast, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from apps.core.database import get_db
from apps.core.exceptions import (
    DatabaseException,
    FazendaNotFoundException,
    InvalidCoordinatesException,
)

from .models_sqla import AreaImovel
from .schemas import (
    BuscaPontoRequest,
    BuscaRaioRequest,
    BuscaRaioResponse,
    FazendaSchema,
)

logger = logging.getLogger(__name__)

router = APIRouter()


def serialize_fazenda(fazenda: AreaImovel) -> dict:
    """Serialize fazenda with latitude and longitude from geometry centroid."""
    data = {
        "gid": fazenda.gid,
        "cod_tema": fazenda.cod_tema,
        "nom_tema": fazenda.nom_tema,
        "cod_imovel": fazenda.cod_imovel,
        "mod_fiscal": fazenda.mod_fiscal,
        "num_area": fazenda.num_area,
        "ind_status": fazenda.ind_status,
        "ind_tipo": fazenda.ind_tipo,
        "des_condic": fazenda.des_condic,
        "municipio": fazenda.municipio,
        "cod_estado": fazenda.cod_estado,
        "dat_criaca": fazenda.dat_criaca,
        "dat_atuali": fazenda.dat_atuali,
        "latitude": None,
        "longitude": None,
    }

    # Extract centroid coordinates from geometry
    if fazenda.geom:
        try:
            shape = to_shape(fazenda.geom)
            centroid = shape.centroid
            data["latitude"] = centroid.y
            data["longitude"] = centroid.x
        except Exception as e:
            logger.warning(
                f"Could not extract centroid for fazenda {fazenda.gid}: {str(e)}"
            )

    return data


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
    """Get farm by GID."""
    try:
        logger.info(f"Buscando fazenda com GID: {gid}")
        fazenda = db.query(AreaImovel).filter(AreaImovel.gid == gid).first()

        if not fazenda:
            logger.warning(f"Fazenda com GID {gid} não encontrada")
            raise FazendaNotFoundException(gid)

        logger.info(
            f"Fazenda {gid} encontrada: {fazenda.municipio}/{fazenda.cod_estado}"
        )
        return serialize_fazenda(fazenda)

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
    """Search farms that contain a specific point."""
    try:
        logger.info(
            f"Buscando fazendas no ponto: ({request.latitude}, {request.longitude})"
        )
        point_wkt = f"POINT({request.longitude} {request.latitude})"

        # Filter using ST_Contains
        fazendas = (
            db.query(AreaImovel)
            .filter(
                func.ST_Contains(AreaImovel.geom, func.ST_GeomFromText(point_wkt, 4326))
            )
            .all()
        )

        logger.info(f"Encontradas {len(fazendas)} fazendas no ponto especificado")
        return [serialize_fazenda(f) for f in fazendas]

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
    description="Retorna todas as fazendas dentro de um raio (em km) a partir de um ponto central",
    responses={
        200: {"description": "Busca realizada com sucesso"},
        400: {"description": "Parâmetros inválidos"},
        500: {"description": "Erro interno do servidor"},
    },
)
def busca_raio(request: BuscaRaioRequest, db: Session = Depends(get_db)):
    """Search farms within a radius from a point."""
    try:
        logger.info(
            f"Buscando fazendas em raio de {request.raio_km}km do ponto: "
            f"({request.latitude}, {request.longitude})"
        )

        point_wkt = f"POINT({request.longitude} {request.latitude})"
        radius_meters = request.raio_km * 1000

        # Use ST_DWithin casting to Geography for meter-based distance
        fazendas = (
            db.query(AreaImovel)
            .filter(
                func.ST_DWithin(
                    cast(AreaImovel.geom, Geography),
                    cast(func.ST_GeomFromText(point_wkt, 4326), Geography),
                    radius_meters,
                )
            )
            .all()
        )

        logger.info(f"Encontradas {len(fazendas)} fazendas no raio especificado")

        return BuscaRaioResponse(
            count=len(fazendas),
            raio_km=request.raio_km,
            results=[serialize_fazenda(f) for f in fazendas],
        )

    except SQLAlchemyError as e:
        logger.error(f"Erro de banco de dados na busca por raio: {str(e)}")
        raise DatabaseException("Erro ao buscar fazendas no banco de dados")
    except Exception as e:
        logger.error(f"Erro inesperado na busca por raio: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")
