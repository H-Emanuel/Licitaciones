from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from licitaciones.models import Operador, Licitacion, BitacoraLicitacion, Notificacion

class Command(BaseCommand):
    help = 'Migra datos de operador a operador_user usando la relación Operador.user'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando migración de datos operador → operador_user...'))
        
        # Migrar Licitaciones
        licitaciones_migradas = 0
        for licitacion in Licitacion.objects.filter(operador__isnull=False, operador_user__isnull=True):
            if licitacion.operador and licitacion.operador.user:
                licitacion.operador_user = licitacion.operador.user
                licitacion.save()
                licitaciones_migradas += 1
        
        # Migrar BitacoraLicitacion
        bitacoras_migradas = 0
        for bitacora in BitacoraLicitacion.objects.filter(operador__isnull=False, operador_user__isnull=True):
            if bitacora.operador and bitacora.operador.user:
                bitacora.operador_user = bitacora.operador.user
                bitacora.save()
                bitacoras_migradas += 1
        
        # Migrar Notificaciones
        notificaciones_migradas = 0
        for notificacion in Notificacion.objects.filter(operador__isnull=False, operador_user__isnull=True):
            if notificacion.operador and notificacion.operador.user:
                notificacion.operador_user = notificacion.operador.user
                notificacion.save()
                notificaciones_migradas += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Migración de datos completada:')
        )
        self.stdout.write(f'- Licitaciones migradas: {licitaciones_migradas}')
        self.stdout.write(f'- Bitácoras migradas: {bitacoras_migradas}')
        self.stdout.write(f'- Notificaciones migradas: {notificaciones_migradas}')
        
        # Verificar que todos los datos fueron migrados
        licitaciones_pendientes = Licitacion.objects.filter(operador__isnull=False, operador_user__isnull=True).count()
        bitacoras_pendientes = BitacoraLicitacion.objects.filter(operador__isnull=False, operador_user__isnull=True).count()
        notificaciones_pendientes = Notificacion.objects.filter(operador__isnull=False, operador_user__isnull=True).count()
        
        if licitaciones_pendientes == 0 and bitacoras_pendientes == 0 and notificaciones_pendientes == 0:
            self.stdout.write(self.style.SUCCESS('✅ Todos los datos fueron migrados exitosamente'))
        else:
            self.stdout.write(self.style.WARNING(f'⚠️ Datos pendientes:'))
            if licitaciones_pendientes > 0:
                self.stdout.write(f'  - Licitaciones: {licitaciones_pendientes}')
            if bitacoras_pendientes > 0:
                self.stdout.write(f'  - Bitácoras: {bitacoras_pendientes}')
            if notificaciones_pendientes > 0:
                self.stdout.write(f'  - Notificaciones: {notificaciones_pendientes}')
