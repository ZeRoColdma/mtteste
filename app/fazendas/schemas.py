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
    latitude: Optional[float] = Field(
        None, description="Latitude do centróide da fazenda", example=-21.6813
    )
    longitude: Optional[float] = Field(
        None, description="Longitude do centróide da fazenda", example=-50.7479
    )

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
    page: int = Field(1, description="Número da página (começa em 1)", ge=1, example=1)
    page_size: int = Field(
        10, description="Quantidade de resultados por página", ge=1, le=100, example=10
    )

    @field_validator("raio_km")
    @classmethod
    def validate_raio(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Raio deve ser maior que zero")
        if v > 1000:
            raise ValueError("Raio máximo permitido é 1000 km")
        return v

    @field_validator("page_size")
    @classmethod
    def validate_page_size(cls, v: int) -> int:
        if v < 1:
            raise ValueError("Tamanho da página deve ser no mínimo 1")
        if v > 100:
            raise ValueError("Tamanho máximo da página é 100")
        return v


class BuscaRaioResponse(BaseModel):
    """Response schema for radius-based search with pagination."""

    count: int = Field(
        ..., description="Número total de fazendas encontradas", example=25
    )
    page: int = Field(..., description="Página atual", example=1)
    page_size: int = Field(..., description="Tamanho da página", example=10)
    total_pages: int = Field(..., description="Total de páginas", example=3)
    raio_km: float = Field(
        ..., description="Raio de busca utilizado em km", example=10.0
    )
    results: List[FazendaSchema] = Field(
        ..., description="Lista de fazendas encontradas nesta página"
    )
