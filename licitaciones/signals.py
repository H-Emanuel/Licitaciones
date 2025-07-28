from django.db.models.signals import post_save, pre_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Perfil, BitacoraLicitacion, ObservacionBitacora, Notificacion

@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        # Por defecto, asigna rol 'operador'. Cambia si prefieres otro valor por defecto
        Perfil.objects.create(user=instance, rol='operador')

@receiver(post_save, sender=BitacoraLicitacion)
def crear_notificacion_bitacora(sender, instance, created, **kwargs):
    """Crear notificación cuando se crea una nueva entrada en la bitácora"""
    if created and instance.operador_user:
        # Determinar el tipo de notificación basado en el texto
        tipo = 'general'
        if 'observación' in instance.texto.lower():
            tipo = 'observacion'
        elif 'etapa' in instance.texto.lower():
            tipo = 'etapa'
        elif 'cerrada' in instance.texto.lower():
            tipo = 'cerrada'
        elif 'documento' in instance.texto.lower():
            tipo = 'documento'
        
        # Obtener el nombre del operador
        operador_name = instance.operador_user.get_full_name()
        if not operador_name:
            operador_name = instance.operador_user.username
        
        # Crear título descriptivo
        if tipo == 'observacion':
            titulo = f"Nueva observación de {operador_name}"
        elif tipo == 'etapa':
            titulo = f"Cambio de etapa por {operador_name}"
        elif tipo == 'cerrada':
            titulo = f"Licitación cerrada por {operador_name}"
        else:
            titulo = f"Nueva actividad de {operador_name}"
        
        # Crear mensaje descriptivo
        licitacion_info = f"N° {instance.licitacion.numero_pedido}"
        if instance.licitacion.iniciativa:
            licitacion_info += f" - {instance.licitacion.iniciativa[:50]}..."
        
        mensaje = f"Licitación {licitacion_info}\n{instance.texto}"
        
        Notificacion.objects.create(
            tipo=tipo,
            titulo=titulo,
            mensaje=mensaje,
            licitacion=instance.licitacion,
            operador_user=instance.operador_user,
            leida=False
        )

@receiver(post_save, sender=ObservacionBitacora)
def crear_notificacion_observacion(sender, instance, created, **kwargs):
    """Crear notificación específica cuando se agrega una observación"""
    if created and instance.bitacora.operador_user:
        licitacion_info = f"N° {instance.bitacora.licitacion.numero_pedido}"
        if instance.bitacora.licitacion.iniciativa:
            licitacion_info += f" - {instance.bitacora.licitacion.iniciativa[:50]}..."
        
        operador_name = instance.bitacora.operador_user.get_full_name()
        if not operador_name:
            operador_name = instance.bitacora.operador_user.username
        
        Notificacion.objects.create(
            tipo='observacion',
            titulo=f"Nueva observación de {operador_name}",
            mensaje=f"Licitación {licitacion_info}\nObservación: {instance.texto[:100]}...",
            licitacion=instance.bitacora.licitacion,
            operador_user=instance.bitacora.operador_user,
            leida=False
        )

@receiver(pre_save, sender='licitaciones.Licitacion')
def gestionar_transicion_operador(sender, instance, **kwargs):
    """
    Signal para manejar la transición automática de operador cuando se cambia la etapa
    """
    if instance.pk:  # Solo para licitaciones existentes
        try:
            # Obtener la licitación antes del cambio
            licitacion_anterior = sender.objects.get(pk=instance.pk)
            
            # Verificar si hubo cambio de etapa
            if (licitacion_anterior.etapa_fk != instance.etapa_fk and 
                instance.etapa_fk is not None):
                
                # Obtener el operador activo antes del cambio
                operador_anterior = licitacion_anterior.get_operador_activo()
                
                # Obtener el operador activo después del cambio
                # Para esto necesitamos usar la instancia con la nueva etapa
                operador_nuevo = instance.get_operador_activo()
                
                # Si hay cambio de operador activo, crear notificación
                if (operador_anterior != operador_nuevo and 
                    operador_anterior is not None and 
                    operador_nuevo is not None):
                    
                    # Marcar que hubo transición para crear notificación después del save
                    instance._transicion_operador = {
                        'operador_anterior': operador_anterior,
                        'operador_nuevo': operador_nuevo,
                        'etapa_nueva': instance.etapa_fk
                    }
                    
        except sender.DoesNotExist:
            pass

@receiver(post_save, sender='licitaciones.Licitacion')
def crear_notificacion_transicion_operador(sender, instance, created, **kwargs):
    """
    Crear notificación cuando hay transición de operador
    """
    if (not created and 
        hasattr(instance, '_transicion_operador') and 
        instance._transicion_operador):
        
        transicion = instance._transicion_operador
        
        # Crear notificación para el operador anterior
        operador_anterior_name = transicion['operador_anterior'].get_full_name() or transicion['operador_anterior'].username
        operador_nuevo_name = transicion['operador_nuevo'].get_full_name() or transicion['operador_nuevo'].username
        
        licitacion_info = f"N° {instance.numero_pedido}"
        if instance.iniciativa:
            licitacion_info += f" - {instance.iniciativa[:50]}..."
        
        # Notificación para el operador anterior
        Notificacion.objects.create(
            tipo='etapa',
            titulo=f"Licitación transferida a {operador_nuevo_name}",
            mensaje=f"La licitación {licitacion_info} ha sido transferida automáticamente a {operador_nuevo_name} al llegar a la etapa '{transicion['etapa_nueva'].nombre}'.",
            licitacion=instance,
            operador_user=transicion['operador_anterior'],
            leida=False
        )
        
        # Notificación para el operador nuevo
        Notificacion.objects.create(
            tipo='etapa',
            titulo=f"Nueva licitación asignada",
            mensaje=f"La licitación {licitacion_info} ha sido asignada automáticamente a tu gestión al llegar a la etapa '{transicion['etapa_nueva'].nombre}'.",
            licitacion=instance,
            operador_user=transicion['operador_nuevo'],
            leida=False
        )
        
        # Limpiar el atributo temporal
        delattr(instance, '_transicion_operador')
