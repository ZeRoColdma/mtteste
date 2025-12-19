from fastapi import FastAPI

from apps.fazendas.api import router as fazendas_router

app = FastAPI(title="Fazendas API")

app.include_router(fazendas_router, prefix="/fazendas", tags=["Fazendas"])


@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API de Fazendas (Pure FastAPI)"}
