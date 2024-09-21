# Generated by Django 4.2.16 on 2024-09-21 21:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('formularios', '0014_perfilusuario_remove_tipousuario_descripcion_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='archivoexcel',
            name='procesado',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='archivoexcel',
            name='usuario',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]
