from typing import List, Optional

from pydantic import BaseModel


class FazendaSchema(BaseModel):
    gid: int
    cod_imovel: Optional[str] = None
    nom_tema: Optional[str] = None
    municipio: Optional[str] = None
    cod_estado: Optional[str] = None

    class Config:
        from_attributes = True


class BuscaPontoRequest(BaseModel):
    latitude: float
    longitude: float


class BuscaRaioRequest(BaseModel):
    latitude: float
    longitude: float
    raio_km: float


class BuscaRaioResponse(BaseModel):
    count: int
    raio_km: float
    results: List[FazendaSchema]
