import logging

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class FazendaNotFoundException(HTTPException):
    """Exception raised when a fazenda is not found."""

    def __init__(self, gid: int):
        super().__init__(
            status_code=404, detail=f"Fazenda com GID {gid} não encontrada"
        )


class InvalidCoordinatesException(HTTPException):
    """Exception raised when coordinates are invalid."""

    def __init__(self, message: str = "Coordenadas inválidas"):
        super().__init__(status_code=400, detail=message)


class DatabaseException(HTTPException):
    """Exception raised when database operation fails."""

    def __init__(self, message: str = "Erro ao acessar banco de dados"):
        super().__init__(status_code=500, detail=message)


async def database_exception_handler(request: Request, exc: DatabaseException):
    """Handle database exceptions with proper logging."""
    logger.error(f"Database error on {request.url}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "type": "database_error"},
    )


async def validation_exception_handler(
    request: Request, exc: InvalidCoordinatesException
):
    """Handle validation exceptions."""
    logger.warning(f"Validation error on {request.url}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "type": "validation_error"},
    )
