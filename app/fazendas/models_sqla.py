from geoalchemy2 import Geometry
from sqlalchemy import Column, Index, Integer, String

from app.core.database import Base


class AreaImovel(Base):
    """Model for farm areas with spatial data."""

    __tablename__ = "area_imovel_1"

    gid = Column(Integer, primary_key=True, index=True)
    cod_tema = Column(String(254))
    nom_tema = Column(String(254))
    cod_imovel = Column(String(254), index=True)
    mod_fiscal = Column(String(254))
    num_area = Column(String(254))
    ind_status = Column(String(254), index=True)
    ind_tipo = Column(String(254))
    des_condic = Column(String(254))
    municipio = Column(String(254), index=True)
    cod_estado = Column(String(254), index=True)
    dat_criaca = Column(String(254))
    dat_atuali = Column(String(254))
    geom = Column(Geometry("MULTIPOLYGON", srid=4326))

    __table_args__ = (
        # Spatial index for geometry column (PostGIS will create this automatically)
        Index("idx_area_imovel_geom", "geom", postgresql_using="gist"),
        # Composite index for common queries
        Index("idx_municipio_estado", "municipio", "cod_estado"),
    )

    def __repr__(self):
        return f"<AreaImovel(gid={self.gid}, cod_imovel='{self.cod_imovel}', municipio='{self.municipio}')>"
