from django.urls import path

from . import views

urlpatterns = [
    path("<int:id>/", views.fazenda_detail, name="fazenda_detail"),
    path("busca-ponto/", views.busca_ponto, name="busca_ponto"),
    path("busca-raio/", views.busca_raio, name="busca_raio"),
]
