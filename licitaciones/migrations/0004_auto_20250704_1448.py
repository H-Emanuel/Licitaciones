# Generated by Django 3.2.15 on 2025-07-04 18:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('licitaciones', '0003_notificacion'),
    ]

    operations = [
        migrations.AddField(
            model_name='licitacion',
            name='direccion',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Dirección'),
        ),
        migrations.AddField(
            model_name='licitacion',
            name='institucion',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Institución'),
        ),
    ]
