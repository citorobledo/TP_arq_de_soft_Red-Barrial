from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("entregas", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="entrega",
            name="nombre_referente",
            field=models.CharField(
                blank=True, db_column="NombreReferente", default="", max_length=100
            ),
        ),
    ]