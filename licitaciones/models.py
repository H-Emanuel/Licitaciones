from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver



class Etapa(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Estado(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre

class TipoLicitacion(models.Model):
    nombre = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.nombre

class Moneda(models.Model):
    nombre = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.nombre
    
class Categoria(models.Model):
    nombre = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.nombre
    
class Financiamiento(models.Model):
    nombre = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.nombre

class Departamento(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

class Licitacion(models.Model):
    class Meta:
        db_table = 'licitacion_licitacion'
    
    LLAMADO_COTIZACION_CHOICES = [
        ('primer_llamado', 'Primer llamado'),
        ('segundo_llamado', 'Segundo llamado'),
        ('tercer_llamado', 'Tercer llamado'),
        ('cuarto_llamado', 'Cuarto llamado'),
        ('quinto_llamado', 'Quinto llamado'),
    ]

    TIPO_PRESUPUESTO_CHOICES = [
        ('le', 'LE'),
        ('lp', 'LP'),
        ('lr', 'LR'),
    ]
    
    id = models.AutoField(primary_key=True)  
    operador_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='licitaciones_asignadas', verbose_name="Operador 1")
    operador_2 = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='licitaciones_operador_2', verbose_name="Operador 2")
    etapa_fk = models.ForeignKey('Etapa', on_delete=models.SET_NULL, null=True, blank=True, related_name='proyectos_etapa')
    estado_fk = models.ForeignKey('Estado', on_delete=models.SET_NULL, null=True, blank=True, related_name='proyectos_estado')
    tipo_licitacion = models.ForeignKey('TipoLicitacion', on_delete=models.PROTECT, related_name='licitaciones')
    moneda = models.ForeignKey('Moneda', on_delete=models.PROTECT, related_name='licitaciones', null=True, blank=True)
    numero_pedido = models.IntegerField(verbose_name="N° de pedido")
    id_mercado_publico = models.CharField(max_length=50, blank=True, null=True, verbose_name="ID Mercado Público")
    categoria = models.ForeignKey('Categoria', on_delete=models.PROTECT, related_name='licitaciones', null=True, blank=True)
    financiamiento = models.ManyToManyField('Financiamiento', related_name='licitaciones', blank=True)
    numero_cuenta = models.CharField(max_length=30, verbose_name="N° de cuenta")
    en_plan_anual = models.BooleanField(default=False, verbose_name="¿Está en el plan anual?")
    iniciativa = models.CharField(max_length=255, blank=True, null=True)
    departamento = models.ForeignKey('Departamento', on_delete=models.SET_NULL, null=True, blank=True, related_name='licitaciones')
    monto_presupuestado = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Monto Presupuestado")
    llamado_cotizacion = models.CharField(
        max_length=20, 
        choices=LLAMADO_COTIZACION_CHOICES,
        blank=True, 
        null=True, 
        verbose_name="Llamado Cotización"
    )
    tipo_presupuesto = models.CharField(
        max_length=2,
        choices=TIPO_PRESUPUESTO_CHOICES,
        default='le',
        verbose_name="Tipo por presupuesto",
        null=True,
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    fecha_tentativa_cierre = models.DateField(blank=True, null=True, verbose_name="Fecha tentativa de cierre")
    licitacion_fallida_linkeada = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='nuevas_licitaciones', verbose_name="Licitación fallida linkeada")
    direccion = models.CharField(max_length=255, blank=True, null=True, verbose_name="Dirección")
    institucion = models.CharField(max_length=255, blank=True, null=True, verbose_name="Institución")
    pedido_devuelto = models.BooleanField(default=False, verbose_name="Pedido devuelto")
    #informacion_adicional = models.OneToOneField('InformacionAdicional', on_delete=models.SET_NULL, null=True, blank=True, related_name='licitacion', verbose_name="Información adicional")
    # Tipos de licitación fallida (cuando fallida es True)
    TIPO_FALLIDA_CHOICES = [
        ('revocada', 'Revocada'),
        ('anulada', 'Anulada'),
        ('desierta', 'Desierta'),
    ]
    tipo_fallida = models.CharField(
        max_length=10, 
        choices=TIPO_FALLIDA_CHOICES,
        blank=True, 
        null=True, 
        verbose_name="Tipo de Licitación Fallida"
    )

    def __str__(self):
        return self.iniciativa


   # ACA ES PARA EL TEMA DE LAS ETAPAS EN OPERADORES
    def get_operador_activo(self):
        """
        Retorna el operador activo según la etapa actual.
        - Operador 1: Hasta la etapa 'Evaluación de Ofertas' (inclusive)
        - Operador 2: Desde la etapa posterior a 'Evaluación de Ofertas'
        """
        if not self.etapa_fk:
            return self.operador_user
        
        # Obtener todas las etapas del tipo de licitación ordenadas
        etapas_tipo = self.get_etapas_habilitadas()
        
        # Buscar la etapa "Evaluación de Ofertas" dentro de las etapas de este tipo de licitación
        etapa_evaluacion = None
        posicion_actual = -1
        posicion_evaluacion = -1
        
        for i, rel in enumerate(etapas_tipo):
            if rel.etapa.id == self.etapa_fk.id:
                posicion_actual = i
            
            # Buscar la etapa que contenga "evaluación de ofertas" en su nombre  <------
            if 'evaluación de ofertas' in rel.etapa.nombre.lower():
                etapa_evaluacion = rel.etapa
                posicion_evaluacion = i
        
        # Si no se encontró la etapa de evaluación de ofertas, operador 1 por defecto
        if etapa_evaluacion is None or posicion_evaluacion == -1:
            return self.operador_user
        
        # Si estamos en o antes de "Evaluación de Ofertas", operador 1
        # Si estamos después, operador 2
        if posicion_actual <= posicion_evaluacion:
            return self.operador_user
        else:
            return self.operador_2 if self.operador_2 else self.operador_user

    def get_numero_operador_activo(self):
        """
        Retorna 1 o 2 según qué operador está activo actualmente
        """
        operador_activo = self.get_operador_activo()
        if operador_activo == self.operador_2:
            return 2
        return 1

    def puede_operar_usuario(self, usuario):
        """
        Determina si un usuario puede operar en esta licitación según la etapa actual
        """
        if not usuario:
            return False
        
        # Los admin pueden operar siempre
        if hasattr(usuario, 'perfil') and usuario.perfil.rol == 'admin':
            return True
        
        # Verificar si es el operador activo
        operador_activo = self.get_operador_activo()
        return operador_activo == usuario

    def debe_saltar_aprobacion_consejo(self):
        """
        Determina si esta licitación debe saltar la etapa de 'Aprobación del Concejo Municipal'
        cuando tiene moneda UF y monto menor a 500
        """
        if not self.moneda or not self.monto_presupuestado:
            return False
        
        # Verificar si la moneda es UF
        if self.moneda and self.moneda.nombre.upper() == 'UF':
            # Verificar si el monto es menor a 500
            try:
                monto = float(self.monto_presupuestado) if self.monto_presupuestado else 0
                if monto < 500:
                    return True
            except (ValueError, TypeError):
                # Si no se puede convertir a número, no saltar la aprobación
                return False
        
        return False

    def get_etapas_habilitadas(self):
        """
        Retorna las etapas habilitadas para esta licitación,
        excluyendo la aprobación del consejo municipal si aplica
        """
        # Obtener todas las etapas del tipo de licitación a través de la tabla intermedia
        etapas_tipo = list(self.tipo_licitacion.etapas_rel.order_by('orden').all())
        
        # Si debe saltar la aprobación del consejo, filtrarla
        if self.debe_saltar_aprobacion_consejo():
            etapas_tipo = [
                rel for rel in etapas_tipo 
                if 'aprobación del concejo municipal' not in rel.etapa.nombre.lower()
            ]
        
        return etapas_tipo
    
    def get_etapas_todas_con_inhabilitacion(self):
        """
        Retorna todas las etapas del tipo de licitación con información de si están inhabilitadas
        """
        # Obtener todas las etapas del tipo de licitación a través de la tabla intermedia
        etapas_tipo = list(self.tipo_licitacion.etapas_rel.order_by('orden').all())
        
        # Verificar si debe saltar la aprobación del consejo
        debe_saltar_consejo = self.debe_saltar_aprobacion_consejo()
        
        etapas_con_info = []
        for rel in etapas_tipo:
            etapa_info = {
                'rel': rel,
                'etapa': rel.etapa,
                'inhabilitada': False
            }
            
            # Marcar como inhabilitada si es la etapa de aprobación del consejo y debe saltarla
            if debe_saltar_consejo and 'aprobación del concejo municipal' in rel.etapa.nombre.lower():
                etapa_info['inhabilitada'] = True
            
            etapas_con_info.append(etapa_info)
        
        return etapas_con_info













"""

class Adjudicacion(models.Model):
    empresa = models.CharField(max_length=100, unique=True)
    rut = models.CharField(max_length=20, unique=True)
    monto_adjudicado = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    fecha_decreto = models.DateField(blank=True, null=True)
    fecha_subida_mercado_publico = models.DateField(blank=True, null=True)
    orden_compra = models.IntegerField(default=0)

    def __str__(self):
        return self.nombre
    
class Evaluacion(models.Model):
    fecha_evaluacion_tecnica = models.DateField(blank=True, null=True, verbose_name="Fecha de evaluación técnica")
    nombre_integrante_uno = models.CharField(max_length=100, blank=True, null=True)
    nombre_integrante_dos = models.CharField(max_length=100, blank=True, null=True)
    nombre_integrante_tres = models.CharField(max_length=100, blank=True, null=True)
    fecha_comision = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.fecha_evaluacion.strftime('%d/%m/%Y') if self.fecha_evaluacion else "Sin fecha"
    

class PublicacionPortal(models.Model):
    fecha_cierre_preguntas = models.DateField(blank=True, null=True, verbose_name="Fecha de cierre de preguntas")
    fecha_respuesta = models.DateField(blank=True, null=True, verbose_name="Fecha de respuesta")
    fecha_visita_terreno = models.DateField(blank=True, null=True, verbose_name="Fecha de visita a terreno")
    fecha_cierre_oferta = models.DateField(blank=True, null=True, verbose_name="Fecha de cierre de oferta")
    fecha_apertura_tecnica = models.DateField(blank=True, null=True, verbose_name="Fecha de apertura técnica")
    fecha_apertura_economica = models.DateField(blank=True, null=True, verbose_name="Fecha de apertura económica")
    fecha_estimada_adjudicacion = models.DateField(blank=True, null=True, verbose_name="Fecha estimada de adjudicación")

class InformacionAdicional(models.Model):
    adjudicacion = models.OneToOneField(Adjudicacion, on_delete=models.SET_NULL, null=True, blank=True)
    evaluacion = models.OneToOneField(Evaluacion, on_delete=models.SET_NULL, null=True, blank=True)
    publicacion_portal = models.OneToOneField(PublicacionPortal, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_disponibilidad_presupuestaria = models.DateField(blank=True, null=True, verbose_name="Fecha que se pide disponibilidad presupuestaria")
    fecha_comision = models.DateField(blank=True, null=True, verbose_name="Fecha de comisión")
    fecha_solicitud_regimen_interno = models.DateField(blank=True, null=True, verbose_name="Fecha de solicitud de régimen interno")
    fecha_llegada_documento_regimen_interno = models.DateField(blank=True, null=True, verbose_name="Fecha de llegada de documento")
    fecha_tope_firma_contrato = models.DateField(blank=True, null=True, verbose_name="Fecha tope de firma de contrato")

"""

















class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ROL_CHOICES = (
        ('admin', 'Administrador'),
        ('operador', 'Operador'),
    )
    rol = models.CharField(max_length=20, choices=ROL_CHOICES)

    def __str__(self):
        return f"{self.user.username} ({self.rol})"

class BitacoraLicitacion(models.Model):
    licitacion = models.ForeignKey(Licitacion, on_delete=models.CASCADE, related_name='bitacoras')
    # Removed operador field - now using operador_user (User model)
    operador_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='bitacoras_operador')
    texto = models.TextField(verbose_name="Comentario/Acción")
    fecha = models.DateTimeField(auto_now_add=True)
    etapa = models.ForeignKey(Etapa, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.licitacion} - {self.operador_user} - {self.fecha:%d/%m/%Y %H:%M}"

class DocumentoLicitacion(models.Model):
    licitacion = models.ForeignKey(Licitacion, on_delete=models.CASCADE, related_name='documentos')
    archivo = models.FileField(upload_to='documentos_licitacion/')
    nombre = models.CharField(max_length=255, blank=True, null=True)
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre or self.archivo.name

@receiver(post_delete, sender=DocumentoLicitacion)
def eliminar_archivo_documento(sender, instance, **kwargs):
    if instance.archivo:
        instance.archivo.delete(False)

class TipoLicitacionEtapa(models.Model):
    tipo_licitacion = models.ForeignKey(TipoLicitacion, on_delete=models.CASCADE, related_name='etapas_rel')
    etapa = models.ForeignKey(Etapa, on_delete=models.CASCADE, related_name='tipos_licitacion_rel')
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('tipo_licitacion', 'etapa')
        ordering = ['tipo_licitacion', 'orden']

    def __str__(self):
        return f"{self.tipo_licitacion} - {self.etapa} (Orden: {self.orden})"

class ObservacionBitacora(models.Model):
    bitacora = models.OneToOneField(BitacoraLicitacion, on_delete=models.CASCADE, related_name='observacion')
    texto = models.TextField(verbose_name="Observación")
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Obs. {self.bitacora_id}: {self.texto[:40]}..."
    
class DocumentoObservacion(models.Model):
    bitacora = models.ForeignKey(ObservacionBitacora, on_delete=models.CASCADE, related_name='archivos')
    archivo = models.FileField(upload_to='documentos_licitacion/')
    nombre = models.CharField(max_length=255, blank=True, null=True)
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre or self.archivo.name

class DocumentoBitacora(models.Model):
    bitacora = models.ForeignKey(BitacoraLicitacion, on_delete=models.CASCADE, related_name='archivos')
    archivo = models.FileField(upload_to='documentos_licitacion/')
    nombre = models.CharField(max_length=255, blank=True, null=True)
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre or self.archivo.name

class Notificacion(models.Model):
    TIPO_CHOICES = [
        ('observacion', 'Nueva Observación'),
        ('etapa', 'Cambio de Etapa'),
        ('cerrada', 'Licitación Cerrada'),
        ('documento', 'Documento Subido'),
        ('general', 'General'),
    ]
    
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='general')
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    licitacion = models.ForeignKey(Licitacion, on_delete=models.CASCADE, related_name='notificaciones', null=True, blank=True)
    operador_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='notificaciones_operador')
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='notificaciones_admin')
    fecha = models.DateTimeField(auto_now_add=True)
    leida = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.titulo} - {self.fecha.strftime('%d/%m/%Y %H:%M')}"