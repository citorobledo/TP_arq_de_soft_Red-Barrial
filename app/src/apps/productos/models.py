from django.db import models


class Producto(models.Model):
    id = models.BigAutoField(primary_key=True, db_column="ID")
    nombre = models.CharField(max_length=120, unique=True, db_column="Nombre")

    class Meta:
        db_table = "Producto"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
        }
