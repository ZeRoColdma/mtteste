import logging
import sys
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from apps.core.config import get_settings
from apps.core.exceptions import (
    DatabaseException,
    InvalidCoordinatesException,
    database_exception_handler,
    validation_exception_handler,
)
from apps.fazendas.api import router as fazendas_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    logger.info("🚀 Starting Fazendas API...")
    logger.info(f"📊 Database: {settings.POSTGRES_DB}")
    logger.info(f"🔧 Pool size: {settings.DB_POOL_SIZE}")
    yield
    logger.info("👋 Shutting down Fazendas API...")


# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Add compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Request ID middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add unique request ID to each request for tracing."""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = str(process_time)

    logger.info(
        f"Request: {request.method} {request.url.path} | "
        f"Status: {response.status_code} | "
        f"Time: {process_time:.3f}s | "
        f"ID: {request_id}"
    )

    return response


# Exception handlers
app.add_exception_handler(DatabaseException, database_exception_handler)
app.add_exception_handler(InvalidCoordinatesException, validation_exception_handler)


# Health check endpoint
@app.get(
    "/health",
    tags=["Health"],
    summary="Health Check",
    description="Verifica o status da API e conectividade com o banco de dados",
)
async def health_check():
    """Health check endpoint."""
    from sqlalchemy import text

    from apps.core.database import engine

    try:
        # Test database connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "version": settings.API_VERSION,
            "database": "connected",
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "version": settings.API_VERSION,
                "database": "disconnected",
                "error": str(e),
            },
        )


# Root endpoint
@app.get(
    "/",
    tags=["Root"],
    summary="API Root",
    description="Informações básicas sobre a API",
)
def read_root():
    """Root endpoint with API information."""
    return {
        "message": "Bem-vindo à API de Fazendas",
        "version": settings.API_VERSION,
        "docs": "/docs",
        "health": "/health",
    }


# Include routers
app.include_router(fazendas_router, prefix="/fazendas", tags=["Fazendas"])
