from django.core.paginator import Paginator
from django.db.models import Q
from .models import Etapa, Estado, TipoLicitacion, Moneda, Categoria, Financiamiento, Departamento, TipoLicitacionEtapa, Licitacion

def get_filtered_projects_list(base_queryset, request):
    """
    Filtra una queryset de licitaciones según los parámetros de la solicitud.
    Aplica filtros comunes como solo_fallidas, solo_anuales y búsqueda por texto.
    
    Args:
        base_queryset: QuerySet base de Licitacion a filtrar
        request: Objeto request de Django con los parámetros GET
        
    Returns:
        QuerySet filtrado de Licitacion
    """
    # Filtro por estado fallido si corresponde
    solo_fallidas = request.GET.get('solo_fallidas') == '1'
    if solo_fallidas:
        # Buscar estados que puedan indicar "fallido" con diferentes variaciones
        estado_fallido = Estado.objects.filter(
            Q(nombre__iexact='fallido') | 
            Q(nombre__iexact='fallida') | 
            Q(nombre__icontains='fallid')
        ).first()
        if estado_fallido:
            base_queryset = base_queryset.filter(estado_fk=estado_fallido)
    
    # Filtro por plan anual si corresponde
    solo_anuales = request.GET.get('solo_anuales') == '1'
    if solo_anuales:
        base_queryset = base_queryset.filter(en_plan_anual=True)
    
    # Filtro por búsqueda de texto
    q = request.GET.get('q', '').strip()
    if q:
        if q.isdigit():
            base_queryset = base_queryset.filter(id=int(q))
        else:
            base_queryset = base_queryset.filter(iniciativa__icontains=q)
            
    return base_queryset

def get_paginated_projects(projects_list, request, page_size=10):
    """
    Pagina una lista de proyectos según los parámetros de la solicitud.
    
    Args:
        projects_list: QuerySet de Licitacion a paginar
        request: Objeto request de Django con el parámetro page
        page_size: Número de elementos por página (por defecto 10)
        
    Returns:
        Objeto Page con los proyectos paginados
    """
    paginator = Paginator(projects_list, page_size)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)

def get_catalog_data():
    """
    Obtiene los catálogos necesarios para las vistas de licitaciones.
    Centraliza la obtención de etapas, estados, tipos de licitación, etc.
    
    Returns:
        Diccionario con todos los catálogos necesarios para las vistas
    """
    from .models import Licitacion
    
    return {
        'etapas': list(Etapa.objects.all().order_by('id').values('id', 'nombre')),
        'estados': list(Estado.objects.all().order_by('id').values('id', 'nombre')),
        'tipos_licitacion': list(TipoLicitacion.objects.all().order_by('id').values('id', 'nombre')),
        'monedas': list(Moneda.objects.all().order_by('id').values('id', 'nombre')),
        'categorias': list(Categoria.objects.all().order_by('id').values('id', 'nombre')),
        'financiamientos': list(Financiamiento.objects.all().order_by('id').values('id', 'nombre')),
        'departamentos': list(Departamento.objects.all().order_by('id').values('id', 'nombre')),
        'tipos_licitacion_etapa_raw': list(TipoLicitacionEtapa.objects.all().values('tipo_licitacion_id', 'etapa_id', 'orden')),
        'llamado_cotizacion_choices': Licitacion.LLAMADO_COTIZACION_CHOICES,
    }

def get_operator_view_context(operador_user, request, sort_by='-id'):
    """
    Prepara el contexto para una vista de operador.
    Incluye licitaciones donde el usuario es operador_user (OP1) o operador_2 (OP2).
    
    Args:
        operador_user: Objeto User para filtrar proyectos
        request: Objeto request de Django
        sort_by: Campo por el cual ordenar los proyectos (por defecto '-id')
    
    Returns:
        Diccionario con el contexto para la plantilla
    """
    from django.db.models import Q
    
    # Filtrar proyectos donde el usuario es operador_1 o operador_2
    proyectos_list = Licitacion.objects.select_related(
        'operador_user', 'operador_2', 'etapa_fk', 'estado_fk', 'tipo_licitacion',
        'moneda', 'categoria', 'departamento', 'licitacion_fallida_linkeada'
    ).prefetch_related('financiamiento').filter(
        Q(operador_user=operador_user) | Q(operador_2=operador_user)
    ).order_by(sort_by)
    
    # Aplicar filtros comunes
    proyectos_list = get_filtered_projects_list(proyectos_list, request)
    
    # Paginar resultados
    proyectos = get_paginated_projects(proyectos_list, request)
    
    # Obtener nombre del operador para la barra lateral
    operador_sidebar_nombre = operador_user.get_full_name() or operador_user.username if operador_user else None
    
    # Obtener todos los catálogos de datos
    catalogs = get_catalog_data()
      # Construir el contexto para la plantilla
    return {
        'proyectos': proyectos,
        'paginator': proyectos.paginator,
        'operadores': [operador_user] if operador_user else [],
        'es_admin': False,
        'es_operador': True,
        'operador_sidebar_nombre': operador_sidebar_nombre,
        **catalogs  # Incluir todos los catálogos
    }
