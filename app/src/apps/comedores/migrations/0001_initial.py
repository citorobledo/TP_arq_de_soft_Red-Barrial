import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Comedor",
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
                        max_length=150,
                    ),
                ),
                (
                    "codigo",
                    models.CharField(
                        db_column="Codigo",
                        max_length=50,
                        unique=True,
                    ),
                ),
                (
                    "direccion",
                    models.CharField(
                        db_column="Direccion",
                        max_length=255,
                    ),
                ),
                (
                    "usuario",
                    models.ForeignKey(
                        db_column="ID_Usuario",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="comedores",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "Comedor",
                "ordering": ["nombre"],
            },
        ),
    ]
