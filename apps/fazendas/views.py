from core.models import AreaImovel
from django.contrib.gis.db.models import MultiPolygonField
from django.contrib.gis.db.models.functions import Cast
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import FazendaSerializer


@api_view(["GET"])
def fazenda_detail(request, id):
    """
    GET /fazendas/{id}
    Retorna os dados de uma fazenda específica pelo ID.
    """
    try:
        fazenda = AreaImovel.objects.get(gid=id)
        serializer = FazendaSerializer(fazenda)
        return Response(serializer.data)
    except AreaImovel.DoesNotExist:
        return Response(
            {"error": "Fazenda não encontrada"}, status=status.HTTP_404_NOT_FOUND
        )


@api_view(["POST"])
def busca_ponto(request):
    """
    POST /fazendas/busca-ponto
    Recebe coordenadas (latitude/longitude) e retorna a(s) fazenda(s) que contém aquele ponto.
    Body: { "latitude": -23.5505, "longitude": -46.6333 }
    """
    latitude = request.data.get("latitude")
    longitude = request.data.get("longitude")

    if latitude is None or longitude is None:
        return Response(
            {"error": "latitude e longitude são obrigatórios"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        # Create a point from the coordinates (longitude, latitude order for GEOS)
        ponto = Point(float(longitude), float(latitude), srid=4326)

        # Find all farms that contain this point
        fazendas = AreaImovel.objects.filter(geom__contains=ponto)

        serializer = FazendaSerializer(fazendas, many=True)
        return Response({"count": fazendas.count(), "results": serializer.data})
    except (ValueError, TypeError) as e:
        return Response(
            {"error": f"Coordenadas inválidas: {str(e)}"},
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["POST"])
def busca_raio(request):
    """
    POST /fazendas/busca-raio
    Recebe coordenadas + raio em quilômetros e retorna todas as fazendas dentro desse raio.
    Body: { "latitude": -23.5505, "longitude": -46.6333, "raio_km": 50 }
    """
    print("Oi")
    latitude = request.data.get("latitude")
    longitude = request.data.get("longitude")
    raio_km = request.data.get("raio_km")

    if latitude is None or longitude is None or raio_km is None:
        return Response(
            {"error": "latitude, longitude e raio_km são obrigatórios"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        # Create a point from the coordinates
        ponto = Point(float(longitude), float(latitude), srid=4326)

        # Find all farms within the specified radius (in kilometers)
        # Cast to Geography to use meters/km distance relative to earth surface
        fazendas = AreaImovel.objects.annotate(
            geog=Cast("geom", MultiPolygonField(geography=True))
        ).filter(geog__dwithin=(ponto, D(km=float(raio_km))))

        serializer = FazendaSerializer(fazendas, many=True)
        return Response(
            {
                "count": fazendas.count(),
                "raio_km": float(raio_km),
                "results": serializer.data,
            }
        )
    except (ValueError, TypeError) as e:
        return Response(
            {"error": f"Parâmetros inválidos: {str(e)}"},
            status=status.HTTP_400_BAD_REQUEST,
        )
