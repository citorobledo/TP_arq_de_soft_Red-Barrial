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
    ]
