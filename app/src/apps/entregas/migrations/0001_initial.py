import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("deposito", "0001_initial"),
        ("comedores", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Entrega",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        db_column="ID",
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "fecha",
                    models.DateField(db_column="Fecha"),
                ),
                (
                    "estado",
                    models.CharField(
                        choices=[
                            ("registrada", "Registrada"),
                            ("confirmada", "Confirmada"),
                            ("anulada", "Anulada"),
                        ],
                        db_column="Estado",
                        default="registrada",
                        max_length=30,
                    ),
                ),
                (
                    "fecha_registro",
                    models.DateTimeField(
                        auto_now_add=True,
                        db_column="FechaRegistro",
                    ),
                ),
                (
                    "fecha_confirmacion",
                    models.DateTimeField(
                        blank=True,
                        db_column="FechaConfirmacion",
                        null=True,
                    ),
                ),
                (
                    "nombre_voluntario",
                    models.CharField(
                        db_column="NombreVoluntario",
                        max_length=100,
                    ),
                ),
                (
                    "comedor",
                    models.ForeignKey(
                        db_column="ID_Comedor",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="entregas",
                        to="comedores.comedor",
                    ),
                ),
            ],
            options={
                "db_table": "Entrega",
                "ordering": ["-fecha", "-id"],
            },
        ),
        migrations.CreateModel(
            name="DetalleEntrega",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        db_column="ID",
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "cantidad",
                    models.PositiveIntegerField(db_column="Cantidad"),
                ),
                (
                    "lote",
                    models.ForeignKey(
                        db_column="ID_Lote",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="detalles_entrega",
                        to="deposito.lote",
                    ),
                ),
                (
                    "entrega",
                    models.ForeignKey(
                        db_column="ID_Entrega",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="detalles",
                        to="entregas.entrega",
                    ),
                ),
            ],
            options={
                "db_table": "DetalleEntrega",
                "ordering": ["id"],
                "constraints": [
                    models.CheckConstraint(
                        condition=models.Q(("cantidad__gt", 0)),
                        name="detalle_entrega_cantidad_positiva",
                    ),
                ],
            },
        ),
    ]
