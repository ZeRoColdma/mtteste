import logging
import sys
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.exceptions import (
    DatabaseException,
    InvalidCoordinatesException,
    database_exception_handler,
    validation_exception_handler,
)
from app.fazendas.routes import router as fazendas_router

# Configura logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Eventos do ciclo de vida da aplicação."""
    logger.info("🚀 Starting Fazendas API...")
    logger.info(f"📊 Database: {settings.POSTGRES_DB}")
    logger.info(f"🔧 Pool size: {settings.DB_POOL_SIZE}")
    yield
    logger.info("👋 Shutting down Fazendas API...")


# Cria aplicação FastAPI
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Adiciona middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Adiciona middleware de compressão
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Middleware de ID de requisição
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Adiciona ID único a cada requisição para rastreamento."""
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


# Handlers de exceção
app.add_exception_handler(DatabaseException, database_exception_handler)
app.add_exception_handler(InvalidCoordinatesException, validation_exception_handler)


# Endpoint de health check
@app.get(
    "/health",
    tags=["Health"],
    summary="Health Check",
    description="Verifica o status da API e conectividade com o banco de dados",
)
async def health_check():
    """Endpoint de health check."""
    from sqlalchemy import text

    from app.core.database import engine

    try:
        # Testa conexão com banco de dados
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


# Endpoint raiz
@app.get(
    "/",
    tags=["Root"],
    summary="API Root",
    description="Informações básicas sobre a API",
)
def read_root():
    """Endpoint raiz com informações da API."""
    return {
        "message": "Bem-vindo à API de Fazendas",
        "version": settings.API_VERSION,
        "docs": "/docs",
        "health": "/health",
    }


# Inclui routers
app.include_router(fazendas_router, prefix="/fazendas", tags=["Fazendas"])
