from django.conf import settings
from django.db import models


class Comedor(models.Model):
    id = models.BigAutoField(primary_key=True, db_column="ID")
    nombre = models.CharField(max_length=150, db_column="Nombre")
    codigo = models.CharField(max_length=50, unique=True, db_column="Codigo")
    direccion = models.CharField(max_length=255, db_column="Direccion")
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="comedores",
        db_column="ID_Usuario",
    )

    class Meta:
        db_table = "Comedor"
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "codigo": self.codigo,
            "direccion": self.direccion,
            "id_usuario": self.usuario_id,
        }
