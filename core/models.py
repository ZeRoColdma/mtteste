from django.contrib.gis.db import models


class Cliente(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.nome


class AreaImovel(models.Model):
    gid = models.IntegerField(primary_key=True)
    cod_tema = models.CharField(max_length=254, null=True, blank=True)
    nom_tema = models.CharField(max_length=254, null=True, blank=True)
    cod_imovel = models.CharField(max_length=254, null=True, blank=True)
    mod_fiscal = models.CharField(max_length=254, null=True, blank=True)
    num_area = models.CharField(max_length=254, null=True, blank=True)
    ind_status = models.CharField(max_length=254, null=True, blank=True)
    ind_tipo = models.CharField(max_length=254, null=True, blank=True)
    des_condic = models.CharField(max_length=254, null=True, blank=True)
    municipio = models.CharField(max_length=254, null=True, blank=True)
    cod_estado = models.CharField(max_length=254, null=True, blank=True)
    dat_criaca = models.CharField(max_length=254, null=True, blank=True)
    dat_atuali = models.CharField(max_length=254, null=True, blank=True)
    geom = models.MultiPolygonField(srid=4326)

    def __str__(self):
        return f"{self.gid} - {self.cod_imovel}"

    class Meta:
        db_table = "area_imovel_1"
