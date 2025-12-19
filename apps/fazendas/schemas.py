from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class FazendaSchema(BaseModel):
    """Schema for farm (fazenda) data."""

    gid: int = Field(..., description="ID único da fazenda", example=1)
    cod_tema: Optional[str] = Field(None, description="Código do tema")
    nom_tema: Optional[str] = Field(None, description="Nome do tema")
    cod_imovel: Optional[str] = Field(None, description="Código do imóvel")
    mod_fiscal: Optional[str] = Field(None, description="Módulo fiscal")
    num_area: Optional[str] = Field(None, description="Área em hectares")
    ind_status: Optional[str] = Field(None, description="Status do imóvel")
    ind_tipo: Optional[str] = Field(None, description="Tipo do imóvel")
    des_condic: Optional[str] = Field(None, description="Descrição da condição")
    municipio: Optional[str] = Field(
        None, description="Município", example="Adamantina"
    )
    cod_estado: Optional[str] = Field(
        None, description="Código do estado", example="SP"
    )
    dat_criaca: Optional[str] = Field(None, description="Data de criação")
    dat_atuali: Optional[str] = Field(None, description="Data de atualização")

    class Config:
        from_attributes = True


class BuscaPontoRequest(BaseModel):
    """Request schema for point-based search."""

    latitude: float = Field(
        ...,
        description="Latitude do ponto em graus decimais",
        ge=-90,
        le=90,
        example=-21.6813,
    )
    longitude: float = Field(
        ...,
        description="Longitude do ponto em graus decimais",
        ge=-180,
        le=180,
        example=-50.7479,
    )

    @field_validator("latitude")
    @classmethod
    def validate_latitude(cls, v: float) -> float:
        if not -90 <= v <= 90:
            raise ValueError("Latitude deve estar entre -90 e 90 graus")
        return v

    @field_validator("longitude")
    @classmethod
    def validate_longitude(cls, v: float) -> float:
        if not -180 <= v <= 180:
            raise ValueError("Longitude deve estar entre -180 e 180 graus")
        return v


class BuscaRaioRequest(BaseModel):
    """Request schema for radius-based search."""

    latitude: float = Field(
        ...,
        description="Latitude do centro em graus decimais",
        ge=-90,
        le=90,
        example=-21.6813,
    )
    longitude: float = Field(
        ...,
        description="Longitude do centro em graus decimais",
        ge=-180,
        le=180,
        example=-50.7479,
    )
    raio_km: float = Field(
        ..., description="Raio de busca em quilômetros", gt=0, le=1000, example=10.0
    )

    @field_validator("raio_km")
    @classmethod
    def validate_raio(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Raio deve ser maior que zero")
        if v > 1000:
            raise ValueError("Raio máximo permitido é 1000 km")
        return v


class BuscaRaioResponse(BaseModel):
    """Response schema for radius-based search."""

    count: int = Field(..., description="Número de fazendas encontradas", example=5)
    raio_km: float = Field(
        ..., description="Raio de busca utilizado em km", example=10.0
    )
    results: List[FazendaSchema] = Field(
        ..., description="Lista de fazendas encontradas"
    )
