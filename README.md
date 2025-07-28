# Gestión de Licitaciones - Sistema Municipal Avanzado

## Descripción General

Sistema web avanzado desarrollado en Django para la gestión integral de licitaciones municipales. Permite a administradores y operadores registrar, editar, monitorear y seguir el ciclo completo de proyectos de licitación, con funcionalidades modernas de bitácora, estadísticas, cronología y exportación de datos.

## 👨‍💻 Desarrolladores

**Desarrollador Principal** 2025 (Mayo-Julio)
**Nombre:** Cristóbal Andres Astudillo Castillo  
**Email:** Astudillocristobal@gmail.com  
**GitHub:** Akane32 
**LinkedIn:** Cristobal Astudillo Castillo

> *Desarrollador principal responsable de la arquitectura, implementación y diseño del sistema. Contribuyó significativamente al desarrollo de las funcionalidades avanzadas, interfaz moderna y optimización del rendimiento.*

## 🚀 Características Principales

### 📊 **Gestión de Licitaciones**
- **CRUD completo**: Crear, leer, actualizar y eliminar licitaciones
- **Validación inteligente**: Números de pedido únicos, validación de campos
- **Estados dinámicos**: Sistema de estados con badges coloridos
- **Tipos de licitación**: Configuración flexible con etapas específicas
- **Licitaciones fallidas**: Marcado y tipificación de fallas (Revocada, Anulada, Desierta)
- **Vinculación de licitaciones**: Relación entre licitaciones fallidas y nuevas

### 👥 **Sistema de Usuarios y Roles**
- **Administradores**: Control total del sistema
- **Operadores**: Gestión de licitaciones asignadas
- **Autenticación segura**: Login personalizado por rol
- **Perfiles dinámicos**: Información de usuario en sidebar

### 📋 **Bitácora Avanzada**
- **Registro de actividades**: Todas las acciones quedan registradas
- **Archivos adjuntos**: Subida múltiple con drag & drop
- **Control de etapas**: Avance y retroceso de etapas
- **Observaciones**: Comentarios detallados por operador y admin
- **Marcado de fallas**: Funcionalidad para marcar licitaciones como fallidas

### 🎨 **Interfaz Moderna**
- **Diseño responsive**: Adaptable a móviles y tablets
- **Sidebar dinámico**: Navegación intuitiva con información de usuario
- **Badges de estado**: Visualización colorida de estados y tipos
- **Modales interactivos**: Formularios y vistas en ventanas emergentes
- **Animaciones suaves**: Efectos CSS modernos con hover y transiciones
- **Cronología visual**: Timeline de etapas con iconos y estados

### 🔍 **Búsqueda y Filtrado**
- **Buscador global**: Búsqueda por ID o iniciativa en todas las páginas
- **Filtros avanzados**: Por año, estado fallido, operador
- **Botón "Mostrar Todas"**: Limpia filtros con animación moderna
- **Paginación**: Navegación eficiente por grandes volúmenes de datos

### 📈 **Estadísticas y Reportes**
- **Dashboard de métricas**: Gráficos de licitaciones por estado
- **Estadísticas por operador**: Rendimiento individual
- **Cronología por licitación**: Modal con timeline visual
- **Exportación a Excel**: Datos de licitaciones y bitácora

### 🛠️ **Funcionalidades Técnicas**
- **API endpoints**: Para validaciones y datos dinámicos
- **AJAX avanzado**: Actualizaciones sin recarga de página
- **Gestión de archivos**: Subida, validación y descarga
- **Reloj en tiempo real**: En sidebar con actualización automática
- **Versionado de assets**: Cache busting para CSS/JS

## 🗄️ Estructura de Base de Datos

### Modelos Principales

#### **Licitacion** (Modelo central)
```python
- id: Identificador único
- numero_pedido: Número único de licitación
- operador_user: Usuario responsable (ForeignKey a User)
- etapa_fk: Etapa actual (ForeignKey a Etapa)
- estado_fk: Estado actual (ForeignKey a Estado)
- tipo_licitacion: Tipo de licitación (ForeignKey)
- iniciativa: Descripción del proyecto
- departamento: Departamento responsable
- monto_presupuestado: Presupuesto asignado
- en_plan_anual: Boolean para plan anual
- fecha_creacion: Timestamp de creación
- licitacion_fallida_linkeada: Relación a licitación fallida anterior
- tipo_fallida: Tipo de falla (revocada, anulada, desierta)
- direccion: Dirección del proyecto
- institucion: Institución responsable
- numero_cuenta: Número de cuenta contable
- llamado_cotizacion: Tipo de llamado
- moneda: Moneda del presupuesto
- categoria: Categoría de la licitación
- financiamiento: Fuentes de financiamiento (ManyToMany)
```

#### **BitacoraLicitacion** (Historial de actividades)
```python
- id: Identificador único
- proyecto: Licitación asociada (ForeignKey)
- operador: Usuario que registra (ForeignKey a User)
- texto: Comentario o descripción
- archivo: Archivo adjunto (FileField)
- fecha: Timestamp del registro
- etapa: Etapa asociada al registro
- es_admin: Boolean para diferenciar registros de admin
```

#### **Etapa** (Fases del proceso)
```python
- id: Identificador único
- nombre: Nombre de la etapa
- descripcion: Descripción detallada
- orden: Orden en el proceso
```

#### **Estado** (Estados de licitación)
```python
- id: Identificador único
- nombre: Nombre del estado
- descripcion: Descripción del estado
- color: Color para badge (opcional)
```

#### **TipoLicitacion** (Tipos con etapas específicas)
```python
- id: Identificador único
- nombre: Nombre del tipo
- descripcion: Descripción
- etapas: Relación ManyToMany con Etapa
```

#### **Perfil** (Extensión de usuario Django)
```python
- user: Usuario Django (OneToOne)
- rol: Rol del usuario (admin/operador)
- telefono: Teléfono de contacto
- departamento: Departamento de trabajo
```

## 🎨 Mejoras Visuales Implementadas

### **Botones y Controles**
- Gradientes modernos en botones principales
- Efectos ripple en botones de acción
- Animaciones de hover y focus
- Iconos SVG personalizados

### **Tabla de Licitaciones**
- Headers con sorting visual
- Badges coloridos para estados
- Tooltips informativos
- Responsive design completo

### **Modales y Formularios**
- Diseño glassmorphism
- Drag & drop para archivos
- Validación en tiempo real
- Feedback visual de acciones

### **Cronología de Etapas**
- Timeline visual con iconos
- Estados completados/pendientes
- Botones de navegación entre etapas
- Información contextual

## 📁 Estructura del Proyecto

```
django_maqueta/
├── gestion_licitaciones/          # Configuración principal
│   ├── settings.py               # Configuración Django
│   ├── urls.py                  # URLs principales
│   └── wsgi.py                  # WSGI config
├── licitaciones/                 # App principal
│   ├── models.py                # Modelos de datos
│   ├── views.py                 # Vistas y lógica
│   ├── urls.py                  # URLs de la app
│   ├── admin.py                 # Configuración admin
│   ├── signals.py               # Señales Django
│   ├── utils.py                 # Utilidades
│   ├── migrations/              # Migraciones DB
│   ├── static/licitaciones/     # Archivos estáticos
│   │   ├── *.css               # Estilos por vista
│   │   └── *.js                # JavaScript por vista
│   ├── templates/licitaciones/  # Plantillas HTML
│   │   ├── *.html              # Vistas principales
│   │   └── sidebar.html        # Sidebar modular
│   └── templatetags/           # Filtros personalizados
│       └── chile_filters.py    # Formateo chileno
├── documentos_licitacion/       # Archivos subidos
├── staticfiles/                 # Archivos estáticos compilados
├── tests/                       # Scripts de testing manual
│   ├── README.md               # Documentación de tests
│   └── test_etapas_inhabilitadas.py  # Test de etapas inhabilitadas
└── requirements.txt             # Dependencias
```

## 🛠️ Instalación y Configuración

### Requisitos Previos
- Python 3.8+
- PostgreSQL 12+ (recomendado)
- Git

### Instalación
```bash
# Clonar el repositorio
git clone [repository-url]
cd django_maqueta

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar base de datos en settings.py
# Crear base de datos PostgreSQL

# Aplicar migraciones
python manage.py migrate

# Cargar datos iniciales
python manage.py loaddata licitaciones/fixtures/estados.json
python manage.py loaddata licitaciones/fixtures/etapas.json

# Crear superusuario
python manage.py createsuperuser

# Recopilar archivos estáticos
python manage.py collectstatic

# Ejecutar servidor de desarrollo
python manage.py runserver
```

### Configuración de Producción
```bash
# Variables de entorno recomendadas
export DEBUG=False
export SECRET_KEY="tu-clave-secreta-super-segura"
export DATABASE_URL="postgresql://user:pass@localhost/dbname"
export STATIC_ROOT="/path/to/static/files"
export MEDIA_ROOT="/path/to/media/files"
```

## 🔧 Comandos de Gestión Útiles

```bash
# Backup de base de datos
python manage.py dumpdata > backup.json

# Restaurar backup
python manage.py loaddata backup.json

# Crear migraciones tras cambios en modelos
python manage.py makemigrations

# Ver SQL de migraciones
python manage.py sqlmigrate licitaciones 0001

# Shell interactivo
python manage.py shell

# Ejecutar tests automáticos
python manage.py test

# Ejecutar scripts de testing manual
cd tests/
python test_etapas_inhabilitadas.py
```

## 🎯 Funcionalidades Específicas por Rol

### **Administrador**
- ✅ Crear, editar y eliminar licitaciones
- ✅ Ver todas las licitaciones del sistema
- ✅ Gestionar usuarios y operadores
- ✅ Acceso completo a estadísticas
- ✅ Exportar datos a Excel
- ✅ Cerrar licitaciones definitivamente
- ✅ Ver cronología completa de etapas

### **Operador**
- ✅ Ver licitaciones asignadas
- ✅ Agregar observaciones con archivos
- ✅ Avanzar/retroceder etapas
- ✅ Marcar licitaciones como fallidas
- ✅ Ver última observación
- ✅ Acceso a bitácora de sus licitaciones
- ✅ Cerrar licitaciones (con restricciones)

## 🔐 Seguridad Implementada

- **Autenticación robusta**: Control de acceso por rol
- **CSRF Protection**: Tokens en todos los formularios
- **Validación de archivos**: Tipos y tamaños permitidos
- **Sanitización de datos**: Escape de HTML automático
- **Permisos granulares**: Acceso restringido por funcionalidad

## 📊 APIs y Endpoints

```python
# Validación de números de pedido
/api/validar_numero_pedido/?numero_pedido=123

# Etapas por tipo de licitación
/api/licitacion/<id>/etapas/

# Datos para gráficos de estadísticas
/api/estadisticas/datos/

# Exportación de datos
/exportar/excel/licitaciones/
/exportar/excel/bitacora/<licitacion_id>/
```

## 🚀 Tecnologías Utilizadas

- **Backend**: Django 4.x, Python 3.8+
- **Base de Datos**: PostgreSQL 12+
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Estilos**: CSS Grid, Flexbox, Animaciones CSS
- **Iconos**: Emojis, SVG personalizados
- **Archivos**: FileField de Django, validación mime-type
- **Exportación**: openpyxl, xlsxwriter
- **Formateo**: django-humanize, filtros personalizados

## 📝 Próximas Mejoras

- [ ] Notificaciones en tiempo real (WebSockets)
- [ ] Dashboard avanzado con más métricas
- [ ] Integración con APIs externas
- [ ] Módulo de reportes automáticos
- [ ] App móvil complementaria
- [ ] Sistema de comentarios con hilos
- [ ] Integración con sistemas contables


## 📞 Contacto y Soporte

Para soporte técnico, reportes de bugs o solicitudes de nuevas funcionalidades:

- **Email**: []
- **Teléfono**: []
- **Horario**: 



## 📄 Licencia

Este proyecto fue desarrollado específicamente para uso municipal. Todos los derechos reservados.


---

**Desarrollado con ❤️ para la modernización de la gestión municipal**  
*"Cada línea de código fue escrita pensando en mejorar la eficiencia y transparencia de los procesos municipales"* - Cristóbal Andres Astudillo Castillo