from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("comedores", "0002_comedor_usuario_nullable"),
    ]

    operations = [
        migrations.AddField(
            model_name="comedor",
            name="habilitado",
            field=models.BooleanField(db_column="Habilitado", default=True),
        ),
    ]
