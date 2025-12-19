import pytest
from fastapi.testclient import TestClient
from geoalchemy2 import WKTElement
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings
from app.core.database import get_db
from app.fazendas.models_sqla import AreaImovel
from main import app

settings = get_settings()
engine = create_engine(settings.database_url)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    return TestClient(app)


@pytest.fixture
def fazenda(db_session):
    # Create farm with WKT geometry
    # Square from (-1, -1) to (1, 1)
    poly_wkt = "MULTIPOLYGON(((-1 -1, 1 -1, 1 1, -1 1, -1 -1)))"

    fazenda = AreaImovel(
        gid=9999, cod_imovel="CODE123", geom=WKTElement(poly_wkt, srid=4326)
    )
    db_session.add(fazenda)
    db_session.commit()
    db_session.refresh(fazenda)
    return fazenda


def test_get_fazenda(client, fazenda):
    response = client.get(f"/fazendas/{fazenda.gid}")
    assert response.status_code == 200
    assert response.json()["cod_imovel"] == "CODE123"


def test_get_fazenda_not_found(client, db_session):
    response = client.get("/fazendas/8888")
    assert response.status_code == 404


def test_busca_ponto_success(client, fazenda):
    data = {"latitude": 0, "longitude": 0}
    response = client.post("/fazendas/busca-ponto", json=data)
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["gid"] == fazenda.gid


def test_busca_raio_success(client, fazenda):
    # Point very close to center (0,0)
    data = {"latitude": 0.0001, "longitude": 0.0001, "raio_km": 1}
    response = client.post("/fazendas/busca-raio", json=data)
    assert response.status_code == 200
    data_res = response.json()
    assert data_res["count"] >= 1
    assert data_res["results"][0]["gid"] == fazenda.gid
