import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Producto",
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
                    "nombre",
                    models.CharField(
                        db_column="Nombre",
                        max_length=120,
                        unique=True,
                    ),
                ),
            ],
            options={
                "db_table": "Producto",
                "ordering": ["nombre"],
            },
        ),
        migrations.CreateModel(
            name="Lote",
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
                    "numero_lote",
                    models.CharField(
                        db_column="NumeroLote",
                        max_length=50,
                        unique=True,
                    ),
                ),
                (
                    "fecha_vencimiento",
                    models.DateField(db_column="FechaVencimiento"),
                ),
                (
                    "stock",
                    models.PositiveIntegerField(
                        db_column="Stock",
                        default=0,
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
                    "producto",
                    models.ForeignKey(
                        db_column="ID_Producto",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="lotes",
                        to="deposito.producto",
                    ),
                ),
            ],
            options={
                "db_table": "Lote",
                "ordering": ["fecha_vencimiento", "id"],
                "constraints": [
                    models.CheckConstraint(
                        condition=models.Q(("stock__gte", 0)),
                        name="lote_stock_no_negativo",
                    ),
                ],
            },
        ),
    ]
