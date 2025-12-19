"""Camada de repositório para operações de banco de dados de Fazenda."""

import logging
from typing import List, Optional

from geoalchemy2 import Geography
from sqlalchemy import cast, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.fazendas.models_sqla import AreaImovel

logger = logging.getLogger(__name__)


class FazendaRepository:
    """Repositório para operações de banco de dados de Fazenda."""

    def __init__(self, db: Session):
        """Inicializa o repositório com a sessão do banco de dados."""
        self.db = db

    def get_by_id(self, gid: int) -> Optional[AreaImovel]:
        """
        Busca uma fazenda pelo seu GID.

        Args:
            gid: ID da fazenda

        Returns:
            AreaImovel se encontrada, None caso contrário

        Raises:
            SQLAlchemyError: Se ocorrer erro no banco de dados
        """
        try:
            logger.debug(f"Consultando fazenda com GID: {gid}")
            return self.db.query(AreaImovel).filter(AreaImovel.gid == gid).first()
        except SQLAlchemyError as e:
            logger.error(f"Erro no banco de dados ao buscar fazenda {gid}: {str(e)}")
            raise

    def find_by_point(self, latitude: float, longitude: float) -> List[AreaImovel]:
        """
        Encontra todas as fazendas que contêm um ponto específico.

        Args:
            latitude: Latitude do ponto
            longitude: Longitude do ponto

        Returns:
            Lista de fazendas que contêm o ponto

        Raises:
            SQLAlchemyError: Se ocorrer erro no banco de dados
        """
        try:
            point_wkt = f"POINT({longitude} {latitude})"
            logger.debug(
                f"Consultando fazendas que contêm o ponto: ({latitude}, {longitude})"
            )

            fazendas = (
                self.db.query(AreaImovel)
                .filter(
                    func.ST_Contains(
                        AreaImovel.geom, func.ST_GeomFromText(point_wkt, 4326)
                    )
                )
                .all()
            )

            logger.debug(f"Encontradas {len(fazendas)} fazendas que contêm o ponto")
            return fazendas
        except SQLAlchemyError as e:
            logger.error(
                f"Erro no banco de dados ao buscar fazendas por ponto: {str(e)}"
            )
            raise

    def find_by_radius(
        self,
        latitude: float,
        longitude: float,
        radius_km: float,
        offset: int,
        limit: int,
    ) -> tuple[List[AreaImovel], int]:
        """
        Encontra todas as fazendas dentro de um raio a partir de um ponto com paginação.

        Args:
            latitude: Latitude do ponto central
            longitude: Longitude do ponto central
            radius_km: Raio de busca em quilômetros
            offset: Número de registros a pular
            limit: Número máximo de registros a retornar

        Returns:
            Tupla de (lista de fazendas, contagem total)

        Raises:
            SQLAlchemyError: Se ocorrer erro no banco de dados
        """
        try:
            point_wkt = f"POINT({longitude} {latitude})"
            radius_meters = radius_km * 1000

            logger.debug(
                f"Consultando fazendas dentro de {radius_km}km de ({latitude}, {longitude}), "
                f"offset={offset}, limit={limit}"
            )

            # Consulta base
            base_query = self.db.query(AreaImovel).filter(
                func.ST_DWithin(
                    cast(AreaImovel.geom, Geography),
                    cast(func.ST_GeomFromText(point_wkt, 4326), Geography),
                    radius_meters,
                )
            )

            # Obtém contagem total
            total_count = base_query.count()

            # Obtém resultados paginados
            fazendas = base_query.offset(offset).limit(limit).all()

            logger.debug(
                f"Encontradas {total_count} fazendas no total, retornando {len(fazendas)} nesta página"
            )
            return fazendas, total_count

        except SQLAlchemyError as e:
            logger.error(
                f"Erro no banco de dados ao buscar fazendas por raio: {str(e)}"
            )
            raise
