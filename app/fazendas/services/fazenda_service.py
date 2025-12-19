"""Camada de serviço para lógica de negócio de Fazenda."""

import logging
from typing import Optional

from geoalchemy2.shape import to_shape

from app.fazendas.models_sqla import AreaImovel

logger = logging.getLogger(__name__)


class FazendaService:
    """Serviço para lógica de negócio de Fazenda."""

    @staticmethod
    def serialize_fazenda(fazenda: AreaImovel) -> dict:
        """
        Serializa fazenda com latitude e longitude do centróide da geometria.

        Args:
            fazenda: Instância de AreaImovel

        Returns:
            Dicionário com dados da fazenda incluindo coordenadas do centróide
        """
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

        # Extrai coordenadas do centróide da geometria
        if fazenda.geom:
            try:
                shape = to_shape(fazenda.geom)
                centroid = shape.centroid
                data["latitude"] = centroid.y
                data["longitude"] = centroid.x
            except Exception as e:
                logger.warning(
                    f"Não foi possível extrair o centróide da fazenda {fazenda.gid}: {str(e)}"
                )

        return data

    @staticmethod
    def calculate_pagination(
        total_count: int, page: int, page_size: int
    ) -> tuple[int, int]:
        """
        Calcula parâmetros de paginação.

        Args:
            total_count: Número total de registros
            page: Número da página atual (indexado em 1)
            page_size: Número de registros por página

        Returns:
            Tupla de (offset, total_pages)
        """
        offset = (page - 1) * page_size
        total_pages = (
            total_count + page_size - 1
        ) // page_size  # Divisão com arredondamento para cima
        return offset, total_pages
