from django.contrib import admin
from .models import Etapa, Licitacion, Perfil, DocumentoBitacora

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('user', 'rol')
    search_fields = ('user__username', 'rol')
    list_filter = ('rol',)

@admin.register(Licitacion)
class LicitacionAdmin(admin.ModelAdmin):
    list_display = ('numero_pedido', 'iniciativa', 'operador_user', 'operador_2', 'etapa_fk', 'estado_fk', 'get_operador_activo')
    search_fields = ('numero_pedido', 'iniciativa', 'operador_user__username', 'operador_2__username')
    list_filter = ('etapa_fk', 'estado_fk', 'tipo_licitacion', 'moneda')
    raw_id_fields = ('operador_user', 'operador_2')
    
    def get_operador_activo(self, obj):
        operador_activo = obj.get_operador_activo()
        numero = obj.get_numero_operador_activo()
        return f"OP{numero}: {operador_activo}" if operador_activo else "Sin operador"
    get_operador_activo.short_description = 'Operador Activo'

# Removed Operador model - now using Django's User model
admin.site.register(Etapa)
admin.site.register(DocumentoBitacora)
