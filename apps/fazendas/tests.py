from core.models import AreaImovel
from django.contrib.gis.geos import MultiPolygon, Point, Polygon
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class FazendaTests(APITestCase):
    def setUp(self):
        # Create a sample farm (square around 0,0)
        poly = Polygon.from_bbox((-1, -1, 1, 1))
        self.fazenda = AreaImovel.objects.create(
            gid=1, cod_imovel="CODE123", geom=MultiPolygon(poly)
        )

    def test_get_fazenda_detail(self):
        """Test retrieving a specific farm by ID"""
        url = reverse("fazenda_detail", args=[self.fazenda.gid])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["cod_imovel"], "CODE123")

    def test_get_fazenda_detail_not_found(self):
        """Test retrieving a non-existent farm"""
        url = reverse("fazenda_detail", args=[999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_busca_ponto_success(self):
        """Test finding a farm containing a point"""
        url = reverse("busca_ponto")
        # Point (0, 0) is inside the square (-1, -1, 1, 1)
        data = {"latitude": 0, "longitude": 0}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["gid"], self.fazenda.gid)

    def test_busca_ponto_failure(self):
        """Test searching with a point outside the farm"""
        url = reverse("busca_ponto")
        # Point (2, 2) is outside the square
        data = {"latitude": 2, "longitude": 2}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)

    def test_busca_raio_success(self):
        """Test finding a farm within a radius"""
        url = reverse("busca_raio")
        # Point (2, 0) is 2 units away (approx 222km at equator, but simpler: check logic)
        # Using a very large radius to ensure inclusion if distance logic works
        # Point (1.1, 0) is 0.1 deg away from edge (approx 11km)
        data = {"latitude": 0, "longitude": 1.1, "raio_km": 20}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertGreaterEqual(response.data["count"], 1)

    def test_busca_raio_invalid_params(self):
        """Test validation for missing parameters"""
        url = reverse("busca_raio")
        data = {"latitude": 0}  # Missing longitude and raio_km
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
