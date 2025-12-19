from core.models import AreaImovel
from django.contrib.gis.db.models import MultiPolygonField
from django.contrib.gis.db.models.functions import Cast
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from rest_framework import pagination, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import FazendaSerializer


class FazendaPagination(pagination.PageNumberPagination):
    page_size = 3
    page_size_query_param = "page_size"
    max_page_size = 100


class FazendaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AreaImovel.objects.all()
    serializer_class = FazendaSerializer
    pagination_class = FazendaPagination
    lookup_field = "gid"

    @action(detail=False, methods=["post"], url_path="busca-ponto")
    def busca_ponto(self, request):
        """
        POST /fazendas/busca-ponto/
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
            queryset = self.get_queryset().filter(geom__contains=ponto)

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response({"count": queryset.count(), "results": serializer.data})
        except (ValueError, TypeError) as e:
            return Response(
                {"error": f"Coordenadas inválidas: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=False, methods=["post"], url_path="busca-raio")
    def busca_raio(self, request):
        """
        POST /fazendas/busca-raio/
        Recebe coordenadas + raio em quilômetros e retorna todas as fazendas dentro desse raio.
        Body: { "latitude": -23.5505, "longitude": -46.6333, "raio_km": 50 }
        """
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

            # Cast to Geography to use meters/km distance relative to earth surface
            queryset = (
                self.get_queryset()
                .annotate(geog=Cast("geom", MultiPolygonField(geography=True)))
                .filter(geog__dwithin=(ponto, D(km=float(raio_km))))
            )

            page = self.paginate_queryset(queryset)
            if page is not None:
                # Add extra context if needed, but standard pagination response is usually sufficient
                # If we really need 'raio_km' in response, we might need a custom response format,
                # but standard pagination is cleaner.
                serializer = self.get_serializer(page, many=True)
                response = self.get_paginated_response(serializer.data)
                response.data["raio_km"] = float(raio_km)  # Adding meta info back
                return response

            serializer = self.get_serializer(queryset, many=True)
            return Response(
                {
                    "count": queryset.count(),
                    "raio_km": float(raio_km),
                    "results": serializer.data,
                }
            )
        except (ValueError, TypeError) as e:
            return Response(
                {"error": f"Parâmetros inválidos: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
