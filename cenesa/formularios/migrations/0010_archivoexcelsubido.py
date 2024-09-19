# Generated by Django 4.2.16 on 2024-09-19 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('formularios', '0009_alter_stock_cantidad'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArchivoExcelSubido',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('archivo', models.FileField(upload_to='archivos_subidos/')),
                ('fecha_subida', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
