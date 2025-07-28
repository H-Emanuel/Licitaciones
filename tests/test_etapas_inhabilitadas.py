#!/usr/bin/env python
"""
Script para probar la funcionalidad de etapas inhabilitadas
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_licitaciones.settings')
django.setup()

from licitaciones.models import Licitacion, Moneda, TipoLicitacion, Etapa
from decimal import Decimal

def probar_etapas_inhabilitadas():
    print("=== PROBANDO FUNCIONALIDAD DE ETAPAS INHABILITADAS ===\n")
    
    # 1. Verificar que existe la moneda UF
    uf, created = Moneda.objects.get_or_create(nombre='UF')
    print(f"✓ Moneda UF: {uf.nombre} {'(creada)' if created else '(existente)'}")
    
    # 2. Obtener primer tipo de licitación
    tipo = TipoLicitacion.objects.first()
    if not tipo:
        print("❌ No se encontró ningún tipo de licitación")
        return
    
    print(f"✓ Tipo de licitación: {tipo.nombre}")
    
    # 3. Verificar etapas del tipo
    etapas_rel = tipo.etapas_rel.order_by('orden').all()
    print(f"✓ Etapas del tipo '{tipo.nombre}':")
    for rel in etapas_rel:
        print(f"   - {rel.orden}: {rel.etapa.nombre}")
    
    # Buscar etapa de aprobación del consejo
    etapa_consejo = None
    for rel in etapas_rel:
        if 'aprobación del concejo municipal' in rel.etapa.nombre.lower():
            etapa_consejo = rel.etapa
            break
    
    if etapa_consejo:
        print(f"✓ Encontrada etapa del consejo: {etapa_consejo.nombre}")
    else:
        print("⚠️  No se encontró etapa de 'Aprobación del Concejo Municipal'")
    
    # 4. Crear licitación de prueba con UF < 500
    print("\n--- CASO 1: UF con monto < 500 ---")
    
    licitacion_uf_menor = Licitacion.objects.create(
        numero_pedido=99001,
        numero_cuenta='TEST_UF_MENOR',
        iniciativa='Prueba UF menor a 500',
        tipo_licitacion=tipo,
        moneda=uf,
        monto_presupuestado=Decimal('300')  # Menor a 500
    )
    
    print(f"✓ Licitación creada: ID {licitacion_uf_menor.id}")
    print(f"✓ Moneda: {licitacion_uf_menor.moneda.nombre}")
    print(f"✓ Monto: {licitacion_uf_menor.monto_presupuestado}")
    print(f"✓ Debe saltar aprobación del consejo: {licitacion_uf_menor.debe_saltar_aprobacion_consejo()}")
    
    # Verificar etapas con inhabilitación
    etapas_con_info = licitacion_uf_menor.get_etapas_todas_con_inhabilitacion()
    print("✓ Etapas con información de inhabilitación:")
    for etapa_info in etapas_con_info:
        etapa = etapa_info['etapa']
        inhabilitada = etapa_info['inhabilitada']
        status = "🚫 INHABILITADA" if inhabilitada else "✅ Habilitada"
        print(f"   - {etapa.nombre}: {status}")
    
    # 5. Crear licitación de prueba con UF >= 500
    print("\n--- CASO 2: UF con monto >= 500 ---")
    
    licitacion_uf_mayor = Licitacion.objects.create(
        numero_pedido=99002,
        numero_cuenta='TEST_UF_MAYOR',
        iniciativa='Prueba UF mayor o igual a 500',
        tipo_licitacion=tipo,
        moneda=uf,
        monto_presupuestado=Decimal('600')  # Mayor a 500
    )
    
    print(f"✓ Licitación creada: ID {licitacion_uf_mayor.id}")
    print(f"✓ Moneda: {licitacion_uf_mayor.moneda.nombre}")
    print(f"✓ Monto: {licitacion_uf_mayor.monto_presupuestado}")
    print(f"✓ Debe saltar aprobación del consejo: {licitacion_uf_mayor.debe_saltar_aprobacion_consejo()}")
    
    # Verificar etapas con inhabilitación
    etapas_con_info_mayor = licitacion_uf_mayor.get_etapas_todas_con_inhabilitacion()
    print("✓ Etapas con información de inhabilitación:")
    for etapa_info in etapas_con_info_mayor:
        etapa = etapa_info['etapa']
        inhabilitada = etapa_info['inhabilitada']
        status = "🚫 INHABILITADA" if inhabilitada else "✅ Habilitada"
        print(f"   - {etapa.nombre}: {status}")
    
    # 6. Crear licitación con otra moneda
    print("\n--- CASO 3: Otra moneda (no UF) ---")
    
    pesos, _ = Moneda.objects.get_or_create(nombre='CLP')
    
    licitacion_clp = Licitacion.objects.create(
        numero_pedido=99003,
        numero_cuenta='TEST_CLP',
        iniciativa='Prueba CLP',
        tipo_licitacion=tipo,
        moneda=pesos,
        monto_presupuestado=Decimal('300')
    )
    
    print(f"✓ Licitación creada: ID {licitacion_clp.id}")
    print(f"✓ Moneda: {licitacion_clp.moneda.nombre}")
    print(f"✓ Monto: {licitacion_clp.monto_presupuestado}")
    print(f"✓ Debe saltar aprobación del consejo: {licitacion_clp.debe_saltar_aprobacion_consejo()}")
    
    # Limpiar licitaciones de prueba
    print("\n--- LIMPIEZA ---")
    licitacion_uf_menor.delete()
    licitacion_uf_mayor.delete()
    licitacion_clp.delete()
    print("✓ Licitaciones de prueba eliminadas")
    
    print("\n=== PRUEBAS COMPLETADAS ===")

if __name__ == "__main__":
    probar_etapas_inhabilitadas()
