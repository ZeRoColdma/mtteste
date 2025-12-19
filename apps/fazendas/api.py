from typing import List

from fastapi import APIRouter, Depends, HTTPException
from geoalchemy2 import Geography
from sqlalchemy import cast, func
from sqlalchemy.orm import Session

from apps.core.database import get_db

from .models_sqla import AreaImovel
from .schemas import (
    BuscaPontoRequest,
    BuscaRaioRequest,
    BuscaRaioResponse,
    FazendaSchema,
)

router = APIRouter()


@router.get("/{gid}", response_model=FazendaSchema)
def get_fazenda(gid: int, db: Session = Depends(get_db)):
    fazenda = db.query(AreaImovel).filter(AreaImovel.gid == gid).first()
    if not fazenda:
        raise HTTPException(status_code=404, detail="Fazenda não encontrada")
    return fazenda


@router.post("/busca-ponto", response_model=List[FazendaSchema])
def busca_ponto(request: BuscaPontoRequest, db: Session = Depends(get_db)):
    point_wkt = f"POINT({request.longitude} {request.latitude})"

    # Filter using ST_Contains
    fazendas = (
        db.query(AreaImovel)
        .filter(
            func.ST_Contains(AreaImovel.geom, func.ST_GeomFromText(point_wkt, 4326))
        )
        .all()
    )

    return fazendas


@router.post("/busca-raio", response_model=BuscaRaioResponse)
def busca_raio(request: BuscaRaioRequest, db: Session = Depends(get_db)):
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

    return BuscaRaioResponse(
        count=len(fazendas), raio_km=request.raio_km, results=fazendas
    )
