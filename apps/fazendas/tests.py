import pytest
from django.contrib.gis.geos import MultiPolygon, Polygon
from django.urls import reverse
from fazendas.models import AreaImovel
from rest_framework import status


@pytest.fixture
def fazenda(db):
    """Fixture to create a sample farm"""
    poly = Polygon.from_bbox((-1, -1, 1, 1))
    return AreaImovel.objects.create(
        gid=9999, cod_imovel="CODE123", geom=MultiPolygon(poly)
    )


@pytest.mark.django_db
def test_get_fazenda_detail(client, fazenda):
    """Test retrieving a specific farm by ID"""
    url = reverse("fazenda-detail", args=[fazenda.gid])
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["cod_imovel"] == "CODE123"


@pytest.mark.django_db
def test_get_fazenda_detail_not_found(client):
    """Test retrieving a non-existent farm"""
    url = reverse("fazenda-detail", args=[999])
    response = client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_busca_ponto_success(client, fazenda):
    """Test finding a farm containing a point"""
    url = reverse("fazenda-busca-ponto")
    # Point (0, 0) is inside the square (-1, -1, 1, 1)
    data = {"latitude": 0, "longitude": 0}
    response = client.post(url, data, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert response.data["results"][0]["gid"] == fazenda.gid


@pytest.mark.django_db
def test_busca_ponto_failure(client, fazenda):
    """Test searching with a point outside the farm"""
    url = reverse("fazenda-busca-ponto")
    # Point (2, 2) is outside the square
    data = {"latitude": 2, "longitude": 2}
    response = client.post(url, data, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 0


@pytest.mark.django_db
def test_busca_raio_success(client, fazenda):
    """Test finding a farm within a radius"""
    url = reverse("fazenda-busca-raio")
    # Point (1.1, 0) is 0.1 deg away from edge (approx 11km)
    data = {"latitude": 0, "longitude": 1.1, "raio_km": 20}
    response = client.post(url, data, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] >= 1


@pytest.mark.django_db
def test_busca_raio_invalid_params(client):
    """Test validation for missing parameters"""
    url = reverse("fazenda-busca-raio")
    data = {"latitude": 0}  # Missing longitude and raio_km
    response = client.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
