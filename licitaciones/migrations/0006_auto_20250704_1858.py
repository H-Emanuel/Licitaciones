# Generated by Django 3.2.15 on 2025-07-04 22:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('licitaciones', '0005_operador_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='bitacoralicitacion',
            name='operador_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='bitacoras_operador', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='licitacion',
            name='operador_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='licitaciones_asignadas', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='notificacion',
            name='operador_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='notificaciones_operador', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='notificacion',
            name='usuario',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='notificaciones_admin', to=settings.AUTH_USER_MODEL),
        ),
    ]
