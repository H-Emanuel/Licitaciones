# Generated by Django 3.2.15 on 2025-07-05 01:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('licitaciones', '0010_update_llamado_cotizacion_choices'),
    ]

    operations = [
        migrations.AddField(
            model_name='licitacion',
            name='tipo_fallida',
            field=models.CharField(blank=True, choices=[('revocada', 'Revocada'), ('anulada', 'Anulada'), ('desierta', 'Desierta')], max_length=10, null=True, verbose_name='Tipo de Licitación Fallida'),
        ),
    ]
