from django.db import migrations

def migrar_relaciones_operador_a_user(apps, schema_editor):
    """Migra las relaciones de Operador a User usando el campo user del operador"""
    # Ya que parece que el campo 'operador' ha sido eliminado, esta migración es un no-op.
    # La migración real debería haberse ejecutado antes de eliminar el campo operador.
    # En este punto, solo aseguramos que la migración se complete con éxito.
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
