from geoalchemy2 import Geometry
from sqlalchemy import Column, Integer, String

from apps.core.database import Base


class AreaImovel(Base):
    __tablename__ = "area_imovel_1"

    gid = Column(Integer, primary_key=True, index=True)
    cod_tema = Column(String(254), nullable=True)
    nom_tema = Column(String(254), nullable=True)
    cod_imovel = Column(String(254), nullable=True)
    mod_fiscal = Column(String(254), nullable=True)
    num_area = Column(String(254), nullable=True)
    ind_status = Column(String(254), nullable=True)
    ind_tipo = Column(String(254), nullable=True)
    des_condic = Column(String(254), nullable=True)
    municipio = Column(String(254), nullable=True)
    cod_estado = Column(String(254), nullable=True)
    dat_criaca = Column(String(254), nullable=True)
    dat_atuali = Column(String(254), nullable=True)
    # Using Geometry type from GeoAlchemy2 with SRID 4326 (WGS84)
    geom = Column(Geometry("MULTIPOLYGON", srid=4326))

    def __repr__(self):
        return f"<AreaImovel(gid={self.gid}, cod_imovel={self.cod_imovel})>"
