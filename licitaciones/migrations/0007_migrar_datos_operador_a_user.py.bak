from django.db import migrations

def migrar_relaciones_operador_a_user(apps, schema_editor):
    """Migra las relaciones de Operador a User usando el campo user del operador"""
    Operador = apps.get_model('licitaciones', 'Operador')
    Licitacion = apps.get_model('licitaciones', 'Licitacion')
    BitacoraLicitacion = apps.get_model('licitaciones', 'BitacoraLicitacion')
    Notificacion = apps.get_model('licitaciones', 'Notificacion')
    
    # Migrar licitaciones
    for licitacion in Licitacion.objects.all():
        if hasattr(licitacion, 'operador_id') and licitacion.operador_id:
            try:
                operador = Operador.objects.get(id=licitacion.operador_id)
                if operador.user:
                    # Actualizar directamente en la base de datos
                    schema_editor.execute(
                        "UPDATE licitacion_licitacion SET operador_id = %s WHERE id = %s",
                        [operador.user.id, licitacion.id]
                    )
            except Operador.DoesNotExist:
                pass
    
    # Migrar bitácoras
    for bitacora in BitacoraLicitacion.objects.all():
        if hasattr(bitacora, 'operador_id') and bitacora.operador_id:
            try:
                operador = Operador.objects.get(id=bitacora.operador_id)
                if operador.user:
                    schema_editor.execute(
                        "UPDATE licitaciones_bitacoralicitacion SET operador_id = %s WHERE id = %s",
                        [operador.user.id, bitacora.id]
                    )
            except Operador.DoesNotExist:
                pass
    
    # Migrar notificaciones
    for notificacion in Notificacion.objects.all():
        if hasattr(notificacion, 'operador_id') and notificacion.operador_id:
            try:
                operador = Operador.objects.get(id=notificacion.operador_id)
                if operador.user:
                    schema_editor.execute(
                        "UPDATE licitaciones_notificacion SET operador_id = %s WHERE id = %s",
                        [operador.user.id, notificacion.id]
                    )
            except Operador.DoesNotExist:
                pass

def revertir_migracion(apps, schema_editor):
    """Función para revertir la migración si es necesario"""
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('licitaciones', '0006_auto_20250704_1858'),
    ]

    operations = [
        migrations.RunPython(migrar_relaciones_operador_a_user, revertir_migracion),
    ]
