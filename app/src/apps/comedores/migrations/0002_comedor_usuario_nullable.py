from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("comedores", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name="comedor",
            name="usuario",
            field=models.ForeignKey(
                blank=True,
                db_column="ID_Usuario",
                null=True,
                on_delete=models.PROTECT,
                related_name="comedores",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
