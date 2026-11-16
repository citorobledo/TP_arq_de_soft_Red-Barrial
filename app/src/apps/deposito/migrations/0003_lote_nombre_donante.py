from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("deposito", "0002_lote_fecha_ingreso"),
    ]

    operations = [
        migrations.AddField(
            model_name="lote",
            name="nombre_donante",
            field=models.CharField(
                blank=True,
                db_column="NombreDonante",
                default="",
                max_length=150,
            ),
        ),
    ]
