import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("deposito", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="lote",
            name="fecha_ingreso",
            field=models.DateField(
                db_column="FechaDeIngreso",
                default=django.utils.timezone.localdate,
            ),
        ),
    ]
