from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from licitaciones.models import Operador, Licitacion, BitacoraLicitacion, Notificacion

class Command(BaseCommand):
    help = 'Migra operadores existentes a usuarios de Django'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando migración de operadores a usuarios...'))
        
        # 1. Crear usuarios para operadores existentes que no tengan usuario
        operadores_sin_usuario = Operador.objects.filter(user__isnull=True)
        
        for operador in operadores_sin_usuario:
            # Crear username basado en el nombre del operador (sin espacios y en minúscula)
            username = operador.nombre.replace(' ', '_').lower()
            
            # Asegurar que el username sea único
            counter = 1
            original_username = username
            while User.objects.filter(username=username).exists():
                username = f"{original_username}_{counter}"
                counter += 1
            
            # Crear el usuario
            user = User.objects.create_user(
                username=username,
                first_name=operador.nombre.split()[0] if operador.nombre.split() else operador.nombre,
                last_name=' '.join(operador.nombre.split()[1:]) if len(operador.nombre.split()) > 1 else '',
                email=f"{username}@empresa.com",  # Email por defecto
                password=operador.clave if operador.clave else 'password123'  # Usar la clave existente o una por defecto
            )
            
            # Vincular el operador con el usuario
            operador.user = user
            operador.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'Creado usuario "{username}" para operador "{operador.nombre}"')
            )
        
        # 2. Mostrar estadísticas
        total_operadores = Operador.objects.count()
        operadores_con_usuario = Operador.objects.filter(user__isnull=False).count()
        
        self.stdout.write(
            self.style.SUCCESS(f'Migración completada:')
        )
        self.stdout.write(f'- Total operadores: {total_operadores}')
        self.stdout.write(f'- Operadores con usuario: {operadores_con_usuario}')
        
        if total_operadores == operadores_con_usuario:
            self.stdout.write(
                self.style.SUCCESS('✅ Todos los operadores tienen usuarios asociados')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'⚠️ {total_operadores - operadores_con_usuario} operadores sin usuario')
            )
