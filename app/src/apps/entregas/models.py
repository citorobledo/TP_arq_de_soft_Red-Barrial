from django.db import models


class Entrega(models.Model):
    class Estado(models.TextChoices):
        REGISTRADA = "registrada", "Registrada"
        CONFIRMADA = "confirmada", "Confirmada"
        ANULADA = "anulada", "Anulada"

    id = models.BigAutoField(primary_key=True, db_column="ID")
    fecha = models.DateField(db_column="Fecha")
    estado = models.CharField(
        max_length=30,
        choices=Estado.choices,
        default=Estado.REGISTRADA,
        db_column="Estado",
    )
    fecha_registro = models.DateTimeField(auto_now_add=True, db_column="FechaRegistro")
    fecha_confirmacion = models.DateTimeField(
        null=True, blank=True, db_column="FechaConfirmacion"
    )
    nombre_voluntario = models.CharField(max_length=100, db_column="NombreVoluntario")
    comedor = models.ForeignKey(
        "comedores.Comedor",
        on_delete=models.PROTECT,
        related_name="entregas",
        db_column="ID_Comedor",
    )

    class Meta:
        db_table = "Entrega"
        ordering = ["-fecha", "-id"]

    def __str__(self):
        return f"Entrega #{self.id} - {self.comedor.codigo} ({self.estado})"

    def to_dict(self):
        return {
            "id": self.id,
            "fecha": self.fecha.isoformat(),
            "estado": self.estado,
            "fecha_registro": (
                self.fecha_registro.isoformat() if self.fecha_registro else None
            ),
            "fecha_confirmacion": (
                self.fecha_confirmacion.isoformat() if self.fecha_confirmacion else None
            ),
            "nombre_voluntario": self.nombre_voluntario,
            "id_comedor": self.comedor_id,
        }


class DetalleEntrega(models.Model):
    id = models.BigAutoField(primary_key=True, db_column="ID")
    cantidad = models.PositiveIntegerField(db_column="Cantidad")
    lote = models.ForeignKey(
        "deposito.Lote",
        on_delete=models.PROTECT,
        related_name="detalles_entrega",
        db_column="ID_Lote",
    )
    entrega = models.ForeignKey(
        Entrega,
        on_delete=models.CASCADE,
        related_name="detalles",
        db_column="ID_Entrega",
    )

    class Meta:
        db_table = "DetalleEntrega"
        ordering = ["id"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(cantidad__gt=0),
                name="detalle_entrega_cantidad_positiva",
            ),
        ]

    def __str__(self):
        return f"Detalle #{self.id} (Entrega #{self.entrega_id}, Lote {self.lote_id})"

    def to_dict(self):
        return {
            "id": self.id,
            "cantidad": self.cantidad,
            "id_lote": self.lote_id,
            "id_entrega": self.entrega_id,
        }
