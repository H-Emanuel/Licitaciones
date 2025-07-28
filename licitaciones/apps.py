from django.apps import AppConfig


class LicitacionesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'licitaciones'

    def ready(self):
        import licitaciones.signals  # Importa las señales al estar lista la app
