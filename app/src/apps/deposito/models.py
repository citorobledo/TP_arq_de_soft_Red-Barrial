from django.db import models


class Lote(models.Model):
    id = models.BigAutoField(primary_key=True, db_column="ID")
    numero_lote = models.CharField(max_length=50, unique=True, db_column="NumeroLote")
    fecha_vencimiento = models.DateField(db_column="FechaVencimiento")
    stock = models.PositiveIntegerField(default=0, db_column="Stock")
    nombre_voluntario = models.CharField(
        max_length=100, db_column="NombreVoluntario"
    )
    producto = models.ForeignKey(
        "productos.Producto",
        on_delete=models.PROTECT,
        related_name="lotes",
        db_column="ID_Producto",
    )

    class Meta:
        db_table = "Lote"
        ordering = ["fecha_vencimiento", "id"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(stock__gte=0),
                name="lote_stock_no_negativo",
            ),
        ]

    def __str__(self):
        return f"{self.numero_lote} ({self.producto.nombre})"

    def to_dict(self):
        return {
            "id": self.id,
            "numero_lote": self.numero_lote,
            "fecha_vencimiento": self.fecha_vencimiento.isoformat(),
            "stock": self.stock,
            "nombre_producto": self.producto.nombre,
            "nombre_voluntario": self.nombre_voluntario,
            "id_producto": self.producto_id,
        }
