from django.test import TestCase, RequestFactory
from django.http import HttpRequest
from .models import Licitacion, Operador, Etapa, Estado, TipoLicitacion
from .utils import get_filtered_projects_list, get_paginated_projects, get_catalog_data, get_operator_view_context

class UtilsTestCase(TestCase):
    def setUp(self):
        # Crear datos de prueba
        self.etapa = Etapa.objects.create(nombre="Etapa prueba")
        self.estado_normal = Estado.objects.create(nombre="Estado normal")
        self.estado_fallido = Estado.objects.create(nombre="Estado fallido")
        self.operador = Operador.objects.create(nombre="Operador Test", clave="123")
          # Crear tipo de licitación
        self.tipo_licitacion = TipoLicitacion.objects.create(nombre="Tipo Test")
        
        # Crear licitaciones de prueba
        self.licitacion1 = Licitacion.objects.create(
            iniciativa="Licitación 1", 
            operador=self.operador,
            etapa_fk=self.etapa,
            estado_fk=self.estado_normal,
            en_plan_anual=True,
            tipo_licitacion=self.tipo_licitacion,
            numero_pedido=1001,
            numero_cuenta="12345"
        )
        
        self.licitacion2 = Licitacion.objects.create(
            iniciativa="Licitación 2", 
            operador=self.operador,
            etapa_fk=self.etapa,
            estado_fk=self.estado_fallido,
            en_plan_anual=False,
            tipo_licitacion=self.tipo_licitacion,
            numero_pedido=1002,
            numero_cuenta="67890"
        )
        
        self.factory = RequestFactory()
        
    def test_get_filtered_projects_list(self):
        # Probar filtro de fallidas
        request = self.factory.get('/?solo_fallidas=1')
        queryset = Licitacion.objects.all()
        filtered = get_filtered_projects_list(queryset, request)
        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first(), self.licitacion2)
        
        # Probar filtro de plan anual
        request = self.factory.get('/?solo_anuales=1')
        filtered = get_filtered_projects_list(queryset, request)
        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first(), self.licitacion1)
        
        # Probar búsqueda por texto
        request = self.factory.get('/?q=Licitación 1')
        filtered = get_filtered_projects_list(queryset, request)
        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first(), self.licitacion1)
        
    def test_get_paginated_projects(self):
        request = self.factory.get('/')
        queryset = Licitacion.objects.all().order_by('id')
        paginated = get_paginated_projects(queryset, request, page_size=1)
        
        self.assertEqual(paginated.paginator.count, 2)
        self.assertEqual(paginated.paginator.num_pages, 2)
        self.assertEqual(paginated.object_list.count(), 1)
        
    def test_get_catalog_data(self):
        catalogs = get_catalog_data()
        self.assertIn('etapas', catalogs)
        self.assertIn('estados', catalogs)
        self.assertEqual(len(catalogs['etapas']), 1)
        self.assertEqual(len(catalogs['estados']), 2)
        
    def test_get_operator_view_context(self):
        request = self.factory.get('/')
        context = get_operator_view_context(self.operador, request)
        
        self.assertIn('proyectos', context)
        self.assertIn('operadores', context)
        self.assertEqual(context['es_admin'], False)
        self.assertEqual(context['operador_sidebar_nombre'], self.operador.nombre)
        self.assertEqual(context['proyectos'].count(), 2)
