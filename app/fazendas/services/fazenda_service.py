"""Service layer for Fazenda business logic."""

import logging
from typing import Optional

from geoalchemy2.shape import to_shape

from app.fazendas.models_sqla import AreaImovel

logger = logging.getLogger(__name__)


class FazendaService:
    """Service for Fazenda business logic."""

    @staticmethod
    def serialize_fazenda(fazenda: AreaImovel) -> dict:
        """
        Serialize fazenda with latitude and longitude from geometry centroid.

        Args:
            fazenda: AreaImovel instance

        Returns:
            Dictionary with farm data including centroid coordinates
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

    @staticmethod
    def calculate_pagination(
        total_count: int, page: int, page_size: int
    ) -> tuple[int, int]:
        """
        Calculate pagination parameters.

        Args:
            total_count: Total number of records
            page: Current page number (1-indexed)
            page_size: Number of records per page

        Returns:
            Tuple of (offset, total_pages)
        """
        offset = (page - 1) * page_size
        total_pages = (total_count + page_size - 1) // page_size  # Ceiling division
        return offset, total_pages
