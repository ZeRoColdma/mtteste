import json

from core.models import AreaImovel
from rest_framework import serializers


class GeoJSONField(serializers.Field):
    """Custom field to serialize GeoDjango geometry as GeoJSON."""

    def to_representation(self, value):
        if value is None:
            return None
        return json.loads(value.geojson)

    def to_internal_value(self, data):
        # Not needed for read-only operations
        raise NotImplementedError("GeoJSON deserialization not implemented")


class FazendaSerializer(serializers.ModelSerializer):
    geom = GeoJSONField(read_only=True)

    class Meta:
        model = AreaImovel
        fields = [
            "gid",
            "cod_tema",
            "nom_tema",
            "cod_imovel",
            "mod_fiscal",
            "num_area",
            "ind_status",
            "ind_tipo",
            "des_condic",
            "municipio",
            "cod_estado",
            "dat_criaca",
            "dat_atuali",
            "geom",
        ]
