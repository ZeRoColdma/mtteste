"""Repository layer for Fazenda database operations."""

import logging
from typing import List, Optional

from geoalchemy2 import Geography
from sqlalchemy import cast, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.fazendas.models_sqla import AreaImovel

logger = logging.getLogger(__name__)


class FazendaRepository:
    """Repository for Fazenda database operations."""

    def __init__(self, db: Session):
        """Initialize repository with database session."""
        self.db = db

    def get_by_id(self, gid: int) -> Optional[AreaImovel]:
        """
        Get a farm by its GID.

        Args:
            gid: Farm ID

        Returns:
            AreaImovel if found, None otherwise

        Raises:
            SQLAlchemyError: If database error occurs
        """
        try:
            logger.debug(f"Querying farm with GID: {gid}")
            return self.db.query(AreaImovel).filter(AreaImovel.gid == gid).first()
        except SQLAlchemyError as e:
            logger.error(f"Database error getting farm {gid}: {str(e)}")
            raise

    def find_by_point(self, latitude: float, longitude: float) -> List[AreaImovel]:
        """
        Find all farms that contain a specific point.

        Args:
            latitude: Point latitude
            longitude: Point longitude

        Returns:
            List of farms containing the point

        Raises:
            SQLAlchemyError: If database error occurs
        """
        try:
            point_wkt = f"POINT({longitude} {latitude})"
            logger.debug(f"Querying farms containing point: ({latitude}, {longitude})")

            fazendas = (
                self.db.query(AreaImovel)
                .filter(
                    func.ST_Contains(
                        AreaImovel.geom, func.ST_GeomFromText(point_wkt, 4326)
                    )
                )
                .all()
            )

            logger.debug(f"Found {len(fazendas)} farms containing the point")
            return fazendas
        except SQLAlchemyError as e:
            logger.error(f"Database error finding farms by point: {str(e)}")
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
        Find all farms within a radius from a point with pagination.

        Args:
            latitude: Center point latitude
            longitude: Center point longitude
            radius_km: Search radius in kilometers
            offset: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple of (list of farms, total count)

        Raises:
            SQLAlchemyError: If database error occurs
        """
        try:
            point_wkt = f"POINT({longitude} {latitude})"
            radius_meters = radius_km * 1000

            logger.debug(
                f"Querying farms within {radius_km}km of ({latitude}, {longitude}), "
                f"offset={offset}, limit={limit}"
            )

            # Base query
            base_query = self.db.query(AreaImovel).filter(
                func.ST_DWithin(
                    cast(AreaImovel.geom, Geography),
                    cast(func.ST_GeomFromText(point_wkt, 4326), Geography),
                    radius_meters,
                )
            )

            # Get total count
            total_count = base_query.count()

            # Get paginated results
            fazendas = base_query.offset(offset).limit(limit).all()

            logger.debug(
                f"Found {total_count} farms total, returning {len(fazendas)} in this page"
            )
            return fazendas, total_count

        except SQLAlchemyError as e:
            logger.error(f"Database error finding farms by radius: {str(e)}")
            raise
