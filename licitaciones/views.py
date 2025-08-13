"""
SISTEMA DE GESTIÓN DE LICITACIONES MUNICIPALES
===============================================

Archivo: views.py - Vistas principales del sistema
Desarrollador Principal: [Tu Nombre Aquí]
Email: [tu.email@ejemplo.com]
Período de Desarrollo: 2024-2025

Este archivo contiene todas las vistas (views) del sistema de gestión de licitaciones,
incluyendo la lógica de negocio, validaciones, APIs y funcionalidades avanzadas.

Características implementadas:
- Sistema completo de CRUD para licitaciones
- API endpoints para validaciones en tiempo real
- Gestión de archivos con drag & drop
- Sistema de roles (Admin/Operador) con permisos granulares
- Exportación avanzada a Excel
- Bitácora detallada de actividades
- Cronología visual de etapas
- Y muchas más funcionalidades...

Para información detallada sobre el desarrollo, consultar CONTRIBUTORS.md
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.db.models import Count, F
from django.utils import timezone
from django.views.decorators.http import require_POST, require_GET, require_http_methods
from django.contrib import messages
import json
import io
import pandas as pd
from .utils import *
from datetime import datetime
from .models import Licitacion, Etapa, BitacoraLicitacion, Estado, DocumentoLicitacion, TipoLicitacion, Moneda, Categoria, Financiamiento, ObservacionBitacora, Departamento, DocumentoBitacora, Notificacion
from .models import TipoLicitacionEtapa
from django.db import models
from django.http import JsonResponse


@login_required
def gestion_licitaciones(request):
    # Si el usuario es admin, redirige a vista_admin; si es operador, a vista_operador
    perfil = getattr(request.user, 'perfil', None)
    if perfil and (perfil.rol or '').strip().lower() == 'operador':
        return redirect('vista_operador')
    return redirect('vista_admin')

@login_required
@csrf_exempt
def modificar_licitacion(request, licitacion_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        licitacion = Licitacion.objects.get(id=licitacion_id)
        cambios = []
        campos_modificados = []
        valores_antes = {}
        valores_despues = {}
        # Solo actualizar el operador si solo viene ese campo
        if ('operador' in data or 'operador_id' in data) and len(data) == 1:
            operador_id = data.get('operador') or data.get('operador_id')
            operador_user = User.objects.get(id=operador_id) if operador_id else None
            if licitacion.operador_user != operador_user:
                cambios.append(f"Operador: '{licitacion.operador_user}' → '{operador_user}'")
                campos_modificados.append('Operador')
                valores_antes['Operador'] = str(licitacion.operador_user)
                valores_despues['Operador'] = str(operador_user)
            licitacion.operador_user = operador_user
            licitacion.save()
        # Solo actualizar la etapa si solo viene ese campo
        elif 'etapa' in data and len(data) == 1:
            etapa_id = data.get('etapa')
            etapa_obj = Etapa.objects.get(id=etapa_id) if etapa_id else None
            if licitacion.etapa_fk != etapa_obj:
                cambios.append(f"Etapa: '{licitacion.etapa_fk}' → '{etapa_obj}'")
                campos_modificados.append('Etapa')
                valores_antes['Etapa'] = str(licitacion.etapa_fk)
                valores_despues['Etapa'] = str(etapa_obj)
            licitacion.etapa_fk = etapa_obj
            licitacion.save()
        # Solo actualizar el estado si solo viene ese campo
        elif 'estado' in data and len(data) == 1:
            estado_id = data.get('estado')
            estado_obj = Estado.objects.get(id=estado_id) if estado_id else None
            if licitacion.estado_fk != estado_obj:
                cambios.append(f"Estado: '{licitacion.estado_fk}' → '{estado_obj}'")
                campos_modificados.append('Estado')
                valores_antes['Estado'] = str(licitacion.estado_fk)
                valores_despues['Estado'] = str(estado_obj)
            licitacion.estado_fk = estado_obj
            licitacion.save()
        else:
            operador_id = data.get('operador') or data.get('operador_id')
            operador_user = User.objects.get(id=operador_id) if operador_id else None
            if licitacion.operador_user != operador_user:
                cambios.append(f"Operador 1: '{licitacion.operador_user}' → '{operador_user}'")
                campos_modificados.append('Operador 1')
                valores_antes['Operador 1'] = str(licitacion.operador_user)
                valores_despues['Operador 1'] = str(operador_user)
            
            # Manejar operador 2
            operador_2_id = data.get('operador_2')
            operador_2_user = User.objects.get(id=operador_2_id) if operador_2_id else None
            if licitacion.operador_2 != operador_2_user:
                cambios.append(f"Operador 2: '{licitacion.operador_2}' → '{operador_2_user}'")
                campos_modificados.append('Operador 2')
                valores_antes['Operador 2'] = str(licitacion.operador_2)
                valores_despues['Operador 2'] = str(operador_2_user)
            
            iniciativa = data.get('iniciativa', '')
            if licitacion.iniciativa != iniciativa:
                cambios.append(f"Iniciativa: '{licitacion.iniciativa}' → '{iniciativa}'")
                campos_modificados.append('Iniciativa')
                valores_antes['Iniciativa'] = str(licitacion.iniciativa)
                valores_despues['Iniciativa'] = str(iniciativa)
            etapa_id = data.get('etapa')
            etapa_obj = Etapa.objects.get(id=etapa_id) if etapa_id else None
            if licitacion.etapa_fk != etapa_obj:
                cambios.append(f"Etapa: '{licitacion.etapa_fk}' → '{etapa_obj}'")
                campos_modificados.append('Etapa')
                valores_antes['Etapa'] = str(licitacion.etapa_fk)
                valores_despues['Etapa'] = str(etapa_obj)
            # Estado
            estado_obj = licitacion.estado_fk  # Siempre inicializado con el valor actual
            if 'estado' in data:
                estado_id = data.get('estado')
                if estado_id:
                    estado_obj = Estado.objects.get(id=estado_id)
                    if licitacion.estado_fk != estado_obj:
                        cambios.append(f"Estado: '{licitacion.estado_fk}' → '{estado_obj}'")
                        campos_modificados.append('Estado')
                        valores_antes['Estado'] = str(licitacion.estado_fk)
                        valores_despues['Estado'] = str(estado_obj)
                licitacion.estado_fk = estado_obj
            # Departamento
            departamento_id = data.get('departamento')
            departamento_obj = None
            if departamento_id:
                try:
                    departamento_obj = Departamento.objects.get(id=departamento_id)
                except Departamento.DoesNotExist:
                    departamento_obj = None
            if licitacion.departamento != departamento_obj:
                cambios.append(f"Departamento: '{licitacion.departamento}' → '{departamento_obj}'")
                campos_modificados.append('Departamento')
                valores_antes['Departamento'] = str(licitacion.departamento)
                valores_despues['Departamento'] = str(departamento_obj)
            # Monto presupuestado - convertir de forma segura
            monto_presupuestado_input = data.get('monto_presupuestado') or 0
            try:
                monto_actual = float(licitacion.monto_presupuestado)
                monto_nuevo = float(monto_presupuestado_input)
                # Convertir a número para asignar al modelo
                monto_presupuestado = monto_nuevo
            except (ValueError, TypeError):
                # Si no se puede convertir, mantener como está o usar 0
                monto_actual = float(licitacion.monto_presupuestado) if licitacion.monto_presupuestado else 0
                try:
                    monto_nuevo = float(monto_presupuestado_input)
                    monto_presupuestado = monto_nuevo
                except (ValueError, TypeError):
                    monto_nuevo = 0
                    monto_presupuestado = 0
            if monto_actual != monto_nuevo:
                cambios.append(f"Monto Presupuestado: '{licitacion.monto_presupuestado}' → '{monto_presupuestado}'")
                campos_modificados.append('Monto Presupuestado')
                valores_antes['Monto Presupuestado'] = str(licitacion.monto_presupuestado)
                valores_despues['Monto Presupuestado'] = str(monto_presupuestado)
            # --- en_plan_anual ---
            if 'en_plan_anual' in data:
                en_plan_anual = data.get('en_plan_anual', False)
                if isinstance(en_plan_anual, str):
                    en_plan_anual = en_plan_anual.lower() in ['1', 'true', 'sí', 'si']
                elif isinstance(en_plan_anual, int):
                    en_plan_anual = bool(en_plan_anual)
                if licitacion.en_plan_anual != en_plan_anual:
                    cambios.append(f"En plan anual: '{licitacion.en_plan_anual}' → '{en_plan_anual}'")
                    campos_modificados.append('En plan anual')
                    valores_antes['En plan anual'] = str(licitacion.en_plan_anual)
                    valores_despues['En plan anual'] = str(en_plan_anual)
                licitacion.en_plan_anual = en_plan_anual
            
            # --- pedido_devuelto ---
            if 'pedido_devuelto' in data:
                pedido_devuelto = data.get('pedido_devuelto', False)
                if isinstance(pedido_devuelto, str):
                    pedido_devuelto = pedido_devuelto.lower() in ['1', 'true', 'sí', 'si']
                elif isinstance(pedido_devuelto, int):
                    pedido_devuelto = bool(pedido_devuelto)
                if licitacion.pedido_devuelto != pedido_devuelto:
                    cambios.append(f"Pedido devuelto: '{licitacion.pedido_devuelto}' → '{pedido_devuelto}'")
                    campos_modificados.append('Pedido devuelto')
                    valores_antes['Pedido devuelto'] = str(licitacion.pedido_devuelto)
                    valores_despues['Pedido devuelto'] = str(pedido_devuelto)
                licitacion.pedido_devuelto = pedido_devuelto
            licitacion.operador_user = operador_user
            licitacion.operador_2 = operador_2_user
            licitacion.iniciativa = iniciativa
            licitacion.etapa_fk = etapa_obj
            licitacion.estado_fk = estado_obj
            licitacion.departamento = departamento_obj
            licitacion.monto_presupuestado = monto_presupuestado
            licitacion.llamado_cotizacion = data.get('llamado_cotizacion', '')
            # Moneda
            moneda_id = data.get('moneda')
            moneda_obj = Moneda.objects.get(id=moneda_id) if moneda_id else None
            if licitacion.moneda != moneda_obj:
                cambios.append(f"Moneda: '{licitacion.moneda}' → '{moneda_obj}'")
                campos_modificados.append('Moneda')
                valores_antes['Moneda'] = str(licitacion.moneda)
                valores_despues['Moneda'] = str(moneda_obj)
            licitacion.moneda = moneda_obj
            # Categoría
            categoria_id = data.get('categoria')
            categoria_obj = Categoria.objects.get(id=categoria_id) if categoria_id else None
            if licitacion.categoria != categoria_obj:
                cambios.append(f"Categoría: '{licitacion.categoria}' → '{categoria_obj}'")
                campos_modificados.append('Categoría')
                valores_antes['Categoría'] = str(licitacion.categoria)
                valores_despues['Categoría'] = str(categoria_obj)
            licitacion.categoria = categoria_obj
            # Financiamiento
            financiamiento_ids = data.get('financiamiento', [])
            if isinstance(financiamiento_ids, list):
                financiamiento_objs = Financiamiento.objects.filter(id__in=financiamiento_ids)
                current_financiamiento_ids = set(licitacion.financiamiento.values_list('id', flat=True))
                new_financiamiento_ids = set(financiamiento_objs.values_list('id', flat=True))

                if current_financiamiento_ids != new_financiamiento_ids:
                    cambios.append(f"Financiamiento: '{current_financiamiento_ids}' → '{new_financiamiento_ids}'")
                    campos_modificados.append('Financiamiento')
                    valores_antes['Financiamiento'] = str(current_financiamiento_ids)
                    valores_despues['Financiamiento'] = str(new_financiamiento_ids)

                licitacion.financiamiento.set(financiamiento_objs)
            else:
                financiamiento_obj = Financiamiento.objects.get(id=financiamiento_ids) if financiamiento_ids else None
                if licitacion.financiamiento != financiamiento_obj:
                    cambios.append(f"Financiamiento: '{licitacion.financiamiento}' → '{financiamiento_obj}'")
                    campos_modificados.append('Financiamiento')
                    valores_antes['Financiamiento'] = str(licitacion.financiamiento)
                    valores_despues['Financiamiento'] = str(financiamiento_obj)
                licitacion.financiamiento = financiamiento_obj
            # Número de pedido
            numero_pedido = data.get('numero_pedido')
            if numero_pedido is not None and str(licitacion.numero_pedido) != str(numero_pedido):
                cambios.append(f"N° de pedido: '{licitacion.numero_pedido}' → '{numero_pedido}'")
                campos_modificados.append('N° de pedido')
                valores_antes['N° de pedido'] = str(licitacion.numero_pedido)
                valores_despues['N° de pedido'] = str(numero_pedido)
                licitacion.numero_pedido = numero_pedido
            
            # ID Mercado Público
            id_mercado_publico = data.get('id_mercado_publico', '')
            if licitacion.id_mercado_publico != id_mercado_publico:
                cambios.append(f"ID Mercado Público: '{licitacion.id_mercado_publico or '-'}' → '{id_mercado_publico or '-'}'")
                campos_modificados.append('ID Mercado Público')
                valores_antes['ID Mercado Público'] = str(licitacion.id_mercado_publico or '-')
                valores_despues['ID Mercado Público'] = str(id_mercado_publico or '-')
                licitacion.id_mercado_publico = id_mercado_publico
            
            # Número de cuenta
            numero_cuenta = data.get('numero_cuenta', '')
            if licitacion.numero_cuenta != numero_cuenta:
                cambios.append(f"N° de cuenta: '{licitacion.numero_cuenta}' → '{numero_cuenta}'")
                campos_modificados.append('N° de cuenta')
                valores_antes['N° de cuenta'] = str(licitacion.numero_cuenta)
                valores_despues['N° de cuenta'] = str(numero_cuenta)
                licitacion.numero_cuenta = numero_cuenta
            # Tipo de licitación
            tipo_licitacion_id = data.get('tipo_licitacion')
            tipo_licitacion_obj = TipoLicitacion.objects.get(id=tipo_licitacion_id) if tipo_licitacion_id else None
            if tipo_licitacion_obj and licitacion.tipo_licitacion != tipo_licitacion_obj:
                cambios.append(f"Tipo de licitación: '{licitacion.tipo_licitacion}' → '{tipo_licitacion_obj}'")
                campos_modificados.append('Tipo de licitación')
                valores_antes['Tipo de licitación'] = str(licitacion.tipo_licitacion)
                valores_despues['Tipo de licitación'] = str(tipo_licitacion_obj)
                licitacion.tipo_licitacion = tipo_licitacion_obj
            # Llamado cotización
            llamado_cotizacion = data.get('llamado_cotizacion', '')
            if licitacion.llamado_cotizacion != llamado_cotizacion:
                cambios.append(f"Llamado Cotización: '{licitacion.llamado_cotizacion}' → '{llamado_cotizacion}'")
                campos_modificados.append('Llamado Cotización')
                valores_antes['Llamado Cotización'] = str(licitacion.llamado_cotizacion)
                valores_despues['Llamado Cotización'] = str(llamado_cotizacion)
                licitacion.llamado_cotizacion = llamado_cotizacion
            # Dirección
            direccion = data.get('direccion', '')
            if licitacion.direccion != direccion:
                cambios.append(f"Dirección: '{licitacion.direccion}' → '{direccion}'")
                campos_modificados.append('Dirección')
                valores_antes['Dirección'] = str(licitacion.direccion or '')
                valores_despues['Dirección'] = str(direccion)
                licitacion.direccion = direccion
            # Institución
            institucion = data.get('institucion', '')
            if licitacion.institucion != institucion:
                cambios.append(f"Institución: '{licitacion.institucion}' → '{institucion}'")
                campos_modificados.append('Institución')
                valores_antes['Institución'] = str(licitacion.institucion or '')
                valores_despues['Institución'] = str(institucion)
                licitacion.institucion = institucion
            # Tipo por presupuesto
            #tipo_presupuesto = get_tipo_presupuesto(moneda_obj.nombre, monto_presupuestado)
            tipo_presupuesto = data.get('tipo_presupuesto', '')
            if licitacion.tipo_presupuesto != tipo_presupuesto:
                cambios.append(f"Tipo por presupuesto: '{licitacion.tipo_presupuesto}' → '{tipo_presupuesto}'")
                campos_modificados.append('N° de cuenta')
                valores_antes['N° de cuenta'] = str(licitacion.tipo_presupuesto)
                valores_despues['N° de cuenta'] = str(tipo_presupuesto)
                licitacion.tipo_presupuesto = tipo_presupuesto
            # Licitacion fallida linkeada
            licitacion_fallida_linkeada_id = data.get('licitacion_fallida_linkeada')
            licitacion_fallida_linkeada_obj = Licitacion.objects.get(id=licitacion_fallida_linkeada_id) if licitacion_fallida_linkeada_id else None
            if licitacion.licitacion_fallida_linkeada != licitacion_fallida_linkeada_obj and licitacion_fallida_linkeada_obj:
                cambios.append(f"Licitación fallida linkeada: '{licitacion.licitacion_fallida_linkeada.numero_pedido}' → '{licitacion_fallida_linkeada_obj.numero_pedido}'")
                campos_modificados.append('Licitación fallida linkeada')
                valores_antes['Licitación fallida linkeada'] = str(licitacion.licitacion_fallida_linkeada.numero_pedido)
                valores_despues['Licitación fallida linkeada'] = str(licitacion_fallida_linkeada_obj.numero_pedido)
            licitacion.licitacion_fallida_linkeada = licitacion_fallida_linkeada_obj
            # GUARDAR CAMBIOS EN LA BASE DE DATOS
            licitacion.save()
        # Registrar en bitácora si hubo cambios
        if cambios:
            texto_bitacora = "Campos modificados:" + ''.join([
                f"\n- {campo}: '{valores_antes[campo]}' → '{valores_despues[campo]}'"
                for campo in campos_modificados
            ])
            # Financiamiento changes
            if 'Financiamiento' in campos_modificados:
                financiamiento_antes = ', '.join(
                    [f.nombre for f in Financiamiento.objects.filter(id__in=valores_antes['Financiamiento'])]
                )
                financiamiento_despues = ', '.join(
                    [f.nombre for f in Financiamiento.objects.filter(id__in=valores_despues['Financiamiento'])]
                )
                texto_bitacora += f"\n- Financiamiento: '{financiamiento_antes}' → '{financiamiento_despues}'"

            BitacoraLicitacion.objects.create(
                licitacion=licitacion,
                texto=texto_bitacora,
                etapa=licitacion.etapa_fk
            )
        return JsonResponse({'ok': True, 'monto_presupuestado': str(licitacion.monto_presupuestado)})
    return JsonResponse({'ok': False}, status=400)

@login_required
@csrf_exempt
def eliminar_licitacion(request, licitacion_id):
    if request.method == 'POST':
        Licitacion.objects.filter(id=licitacion_id).delete()
        return JsonResponse({'ok': True})
    return JsonResponse({'ok': False}, status=400)

def fecha_creacion_api(request, licitacion_id):
    licitacion = Licitacion.objects.get(id=licitacion_id)
    fecha = licitacion.fecha_creacion
    # Formato: 14/05/2025 16:23
    fecha_formateada = fecha.strftime('%d/%m/%Y %H:%M')
    return JsonResponse({'fecha_creacion_formateada': fecha_formateada})

@login_required
def vista_admin(request):
    # Verificar que el usuario es un administrador
    perfil = getattr(request.user, 'perfil', None)
    if not perfil or (perfil.rol or '').strip().lower() != 'admin':
        return redirect('login')
    # Obtener todas las licitaciones ordenadas por ID descendente
    proyectos_list = Licitacion.objects.select_related(
        'operador_user', 'operador_2', 'etapa_fk', 'estado_fk', 'tipo_licitacion',
        'moneda', 'categoria', 'departamento', 'licitacion_fallida_linkeada'
    ).prefetch_related('financiamiento').order_by('-id')

    # Aplicar filtros comunes (fallidas, anuales, búsqueda)
    proyectos_list = get_filtered_projects_list(proyectos_list, request)
    
    # Paginar resultados
    proyectos = get_paginated_projects(proyectos_list, request)
    
    # Obtener todos los catálogos de datos
    catalogs = get_catalog_data()
    
    # Construir el contexto para la plantilla
    context = {
        'proyectos': proyectos,
        'paginator': proyectos.paginator,
        'operadores': User.objects.filter(perfil__rol='operador'),
        'es_admin': True,
        **catalogs  # Incluir todos los catálogos
    }
    
    return render(request, 'licitaciones/gestion_licitaciones.html', context)

@login_required
def vista_operador(request):
    from .utils import get_operator_view_context
    
    # Verificar que el usuario es un operador
    perfil = getattr(request.user, 'perfil', None)
    if not perfil or (perfil.rol or '').strip().lower() != 'operador':
        return redirect('login')
    
    # Obtener contexto para la vista de operador usando el User actual
    context = get_operator_view_context(request.user, request)
    
    return render(request, 'licitaciones/gestion_licitaciones_operador.html', context)

@login_required
def vista_operador_manual(request):
    from .utils import get_operator_view_context
    
    # Verificar si hay un operador seleccionado manualmente
    operador_user_id = request.session.get('operador_manual_id')
    if not operador_user_id:
        return redirect('login')
    
    # Obtener el User
    from django.contrib.auth.models import User
    operador_user = User.objects.filter(id=operador_user_id).first()
    
    # Obtener contexto para la vista de operador
    context = get_operator_view_context(operador_user, request)
    context['es_operador_manual'] = True
    context['es_operador'] = False
    
    return render(request, 'licitaciones/gestion_licitaciones_operador.html', context)

@login_required
def licitaciones_operador(request):
    from .utils import get_operator_view_context
    
    # Verificar que el usuario es un operador
    perfil = getattr(request.user, 'perfil', None)
    if not perfil or (perfil.rol or '').strip().lower() != 'operador':
        return redirect('login')
    
    # Obtener contexto para la vista de operador ordenando por fecha de creación
    context = get_operator_view_context(request.user, request, sort_by='-fecha_creacion')
    
    return render(request, 'licitaciones/gestion_licitaciones_operador.html', context)

@csrf_exempt
def login_view(request):
    from .models import Perfil
    import logging
    
    if request.method == 'POST':
        login_type = request.POST.get('login_type', 'admin')
        
        if login_type == 'operador':
            # Login de operador como User con perfil operador
            username = request.POST.get('username')
            password = request.POST.get('password')
            
            # Intentar autenticar al usuario
            user = authenticate(request, username=username, password=password)
            
            if user and user.is_authenticated:
                perfil = getattr(user, 'perfil', None)
                # Verificar si el usuario es operador manual
                if perfil and perfil.rol == 'admin':
                    login(request, user)
                    request.session['operador_manual_id'] = user.id
                    return redirect('vista_operador_manual')
                elif perfil and perfil.rol == 'operador':
                    login(request, user)
                    return redirect('vista_operador')
                else:
                    error_msg = 'Usuario no tiene permisos de operador.'
                    return render(request, 'licitaciones/login.html', {
                        'error': error_msg,
                        'login_type': 'operador'
                    })
            else:
                error_msg = 'Credenciales de operador incorrectas.'
                return render(request, 'licitaciones/login.html', {
                    'error': error_msg,
                    'login_type': 'operador'
                })
        
        else:
            # Login de administrador (Django estándar)
            form = AuthenticationForm(request, data=request.POST)
            if form.is_valid():
                user = form.get_user()
                login(request, user)
                try:
                    perfil = user.perfil
                    rol = (perfil.rol or '').strip().lower()
                    if rol == 'admin':
                        return redirect('vista_admin')
                    elif rol == 'operador':
                        return redirect('vista_operador')
                    else:
                        logout(request)
                        return render(request, 'licitaciones/login.html', {
                            'form': form, 
                            'error': f'Rol no válido: {perfil.rol}',
                            'login_type': 'admin'
                        })
                except Perfil.DoesNotExist:
                    logout(request)
                    return render(request, 'licitaciones/login.html', {
                        'form': form, 
                        'error': 'Usuario sin perfil asignado',
                        'login_type': 'admin'
                    })
                except Exception as e:
                    logging.exception('Error en login_view')
                    logout(request)
                    return render(request, 'licitaciones/login.html', {
                        'form': form, 
                        'error': 'Error inesperado en el login. Contacte al administrador.',
                        'login_type': 'admin'
                    })
            else:
                return render(request, 'licitaciones/login.html', {
                    'form': form, 
                    'error': 'Credenciales de administrador incorrectas',
                    'login_type': 'admin'
                })
    
    else:
        form = AuthenticationForm()
    
    return render(request, 'licitaciones/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

#ESTADISTICTICAS
@login_required
def estadisticas_view(request):
    # Verificar que sea admin
    perfil = getattr(request.user, 'perfil', None)
    if not perfil or perfil.rol != 'admin':
        return HttpResponseForbidden("Acceso denegado")
    
    total_licitaciones = Licitacion.objects.count()
    # Contar usuarios con perfil de operador
    total_operadores = User.objects.filter(perfil__rol='operador').count()
    # Licitaciones por operador ahora usando User
    licitaciones_por_operador = (
        User.objects.filter(perfil__rol='operador')
        .annotate(num_licitaciones=Count('licitaciones_asignadas'))
        .annotate(nombre=F('username'))  # Para compatibilidad con template
    )
    licitaciones_por_etapa = (
        Etapa.objects.annotate(num_licitaciones=Count('proyectos_etapa'))
    )
    hace_30_dias = timezone.now() - timezone.timedelta(days=30)
    licitaciones_ultimo_mes = Licitacion.objects.filter(fecha_creacion__gte=hace_30_dias).count()
    
    return render(request, 'licitaciones/estadisticas.html', {
        'total_licitaciones': total_licitaciones,
        'total_operadores': total_operadores,
        'licitaciones_por_operador': licitaciones_por_operador,
        'licitaciones_por_etapa': licitaciones_por_etapa,
        'licitaciones_ultimo_mes': licitaciones_ultimo_mes,
        'es_admin': True,
        'es_operador': False,
        'es_operador_manual': False,
        'operador_sidebar_nombre': None,
    })

def logout_operador_manual(request):
    if 'operador_manual_id' in request.session:
        del request.session['operador_manual_id']
    return redirect('login')

def es_usuario_operador(user):
    """
    Función auxiliar para verificar si un usuario es operador
    """
    if not user or not user.is_authenticated:
        return False
    
    # Verificar si tiene perfil de operador
    try:
        if hasattr(user, 'perfil') and user.perfil.rol == 'operador':
            return True
    except AttributeError:
        pass
    
    # Verificar si está asignado como operador en alguna licitación
    from .models import Licitacion
    if Licitacion.objects.filter(operador_user=user).exists() or Licitacion.objects.filter(operador_2=user).exists():
        return True
    
    return False

def bitacora_licitacion(request, licitacion_id):
    # Permitir acceso a admin y operadores (solo lectura para operadores)
    user_rol = None
    es_admin = False
    es_operador = False
    es_operador_manual = False
    operador_sidebar_nombre = None
    
    # Verificar si el usuario está autenticado
    if not request.user.is_authenticated:
        return HttpResponseForbidden('Debe iniciar sesión para acceder a la bitácora.')
    
    # Verificar si viene desde la vista de operador
    from_operador = request.GET.get('from') == 'operador'
    
    # Método 1: Verificar perfil del usuario
    try:
        if hasattr(request.user, 'perfil') and request.user.perfil:
            rol = getattr(request.user.perfil, 'rol', '').strip().lower()
            if rol == 'admin':
                es_admin = True
                user_rol = 'admin'
            elif rol == 'operador':
                es_operador = True
                user_rol = 'operador'
                operador_sidebar_nombre = request.user.get_full_name() or request.user.username
    except (AttributeError, Exception):
        pass
    
    # Método 2: Verificar si es operador por función auxiliar
    if not (es_admin or es_operador) and es_usuario_operador(request.user):
        es_operador = True
        user_rol = 'operador'
        operador_sidebar_nombre = request.user.get_full_name() or request.user.username
    
    # Método 3: Verificar sessions de respaldo
    if not (es_admin or es_operador):
        if 'operador_id' in request.session:
            es_operador = True
            user_rol = 'operador'
            # Legacy session handling - get user by ID
            operador_user = User.objects.filter(id=request.session['operador_id']).first()
            if operador_user:
                operador_sidebar_nombre = operador_user.get_full_name() or operador_user.username
        elif 'operador_manual_id' in request.session:
            es_operador_manual = True
            user_rol = 'operador_manual'
            # Manual operador session handling - get user by ID
            operador_user = User.objects.filter(id=request.session['operador_manual_id']).first()
            if operador_user:
                operador_sidebar_nombre = operador_user.get_full_name() or operador_user.username
    
    # Método 4: Si viene de vista de operador y está autenticado, permitir acceso
    if not (es_admin or es_operador or es_operador_manual) and from_operador:
        es_operador = True
        user_rol = 'operador'
        operador_sidebar_nombre = request.user.get_full_name() or request.user.username
    
    # Si no es admin ni operador, denegar acceso
    if not (es_admin or es_operador or es_operador_manual):
        return HttpResponseForbidden('Solo administradores u operadores pueden acceder a la bitácora.')
    
    licitacion = get_object_or_404(Licitacion, id=licitacion_id)
    bitacora_qs = BitacoraLicitacion.objects.filter(licitacion=licitacion).order_by('-fecha')
    from django.core.paginator import Paginator
    page_number = request.GET.get('page')
    paginator = Paginator(bitacora_qs, 10)
    bitacoras = paginator.get_page(page_number)
    if request.method == 'POST' and (es_admin or es_operador or es_operador_manual):
        # Verificar permisos para operadores
        if (es_operador or es_operador_manual) and not licitacion.puede_operar_usuario(request.user):
            return JsonResponse({
                'ok': False, 
                'error': f'Solo el operador activo puede agregar entradas. Operador activo actual: {licitacion.get_operador_activo()}'
            }, status=403)
        
        texto = request.POST.get('texto', '').strip()
        archivo = request.FILES.get('archivo')
        etapa_id = request.POST.get('etapa')
        id_mercado_publico = request.POST.get('id_mercado_publico', '').strip()
        
        # Campos específicos para Recepción de Ofertas
        numero_ofertas = request.POST.get('numero_ofertas', '').strip()
        empresa_nombre = request.POST.get('empresa_nombre', '').strip()
        empresa_rut = request.POST.get('empresa_rut', '').strip()
        
        etapa_obj = None
        if etapa_id:
            try:
                etapa_obj = Etapa.objects.get(id=etapa_id)
            except Etapa.DoesNotExist:
                etapa_obj = None
        
        # Manejar avance/retroceso de etapa
        accion_etapa = request.POST.get('accion_etapa')
        if accion_etapa == 'advance' and etapa_obj:
            licitacion.etapa_fk = etapa_obj
            licitacion.save()
        elif accion_etapa == 'retreat' and etapa_obj:
            licitacion.etapa_fk = etapa_obj
            licitacion.save()
        
        # Actualizar ID Mercado Público si se proporciona
        if id_mercado_publico:
            licitacion.id_mercado_publico = id_mercado_publico
            licitacion.save()
        
        operador_user = None
        if es_admin:
            operador_user = request.user
        elif es_operador or es_operador_manual:
            operador_user = request.user
            
        if texto or archivo:
            # Agregar información específica de etapa al texto
            texto_completo = texto
            
            # Si es la etapa de Recepción de Ofertas y se proporcionaron datos específicos
            if etapa_obj and 'recepcion' in etapa_obj.nombre.lower() and 'ofertas' in etapa_obj.nombre.lower():
                info_adicional = []
                
                if numero_ofertas:
                    info_adicional.append(f"📊 Ofertas recibidas: {numero_ofertas}")
                
                if empresa_nombre:
                    info_adicional.append(f"🏢 Empresa: {empresa_nombre}")
                
                if empresa_rut:
                    info_adicional.append(f"🆔 RUT: {empresa_rut}")
                
                if info_adicional:
                    if texto_completo:
                        texto_completo += "\n\n" + "\n".join(info_adicional)
                    else:
                        texto_completo = "\n".join(info_adicional)
            
            bitacora = BitacoraLicitacion.objects.create(
                licitacion=licitacion,
                operador_user=operador_user,
                texto=texto_completo,
                etapa=etapa_obj
            )
            
            # Manejar archivos múltiples
            archivos = request.FILES.getlist('archivos')
            if archivos:
                from .models import DocumentoBitacora
                for archivo in archivos:
                    DocumentoBitacora.objects.create(
                        bitacora=bitacora,
                        archivo=archivo,
                        nombre=archivo.name
                    )
            
            # Manejar marcado como fallida
            marcar_fallida = request.POST.get('marcar_fallida') == 'on'
            if marcar_fallida:
                tipo_fallida = request.POST.get('tipo_fallida')
                if tipo_fallida:
                    licitacion.tipo_fallida = tipo_fallida
                    licitacion.save()
            
            return redirect('bitacora_licitacion', licitacion_id=licitacion_id)
    tipo_licitacion = licitacion.tipo_licitacion
    if tipo_licitacion:
        etapas_ids = list(TipoLicitacionEtapa.objects.filter(tipo_licitacion=tipo_licitacion).order_by('orden').values_list('etapa_id', flat=True))
        etapas_qs = Etapa.objects.filter(id__in=etapas_ids).order_by(models.Case(*[models.When(id=pk, then=pos) for pos, pk in enumerate(etapas_ids)]))
        etapas = list(etapas_qs.values('id', 'nombre'))
    else:
        etapas = list(Etapa.objects.order_by('id').values('id', 'nombre'))
    return render(request, 'licitaciones/bitacora_licitacion.html', {
        'licitacion': licitacion,
        'bitacoras': bitacoras,
        'etapas': etapas,
        'es_admin': es_admin,
        'es_operador_manual': es_operador_manual,
        'es_operador': es_operador,
        'paginator': paginator,
        'operador_sidebar_nombre': operador_sidebar_nombre,
    })

@require_POST
@login_required
def subir_documentos_licitacion(request, licitacion_id):
    licitacion = get_object_or_404(Licitacion, id=licitacion_id)
    archivos = request.FILES.getlist('documentos')
    docs = []
    
    # Obtener nombres de documentos existentes para esta licitación
    nombres_existentes = set(
        DocumentoLicitacion.objects.filter(licitacion=licitacion).values_list('nombre', flat=True)
    )
    
    for archivo in archivos:
        # Verificar si ya existe un documento con este nombre
        nombre_archivo = archivo.name
        if nombre_archivo in nombres_existentes:
            # Evitar crear duplicados
            continue
            
        doc = DocumentoLicitacion.objects.create(
            licitacion=licitacion,
            archivo=archivo,
            nombre=nombre_archivo
        )
        nombres_existentes.add(nombre_archivo)
        docs.append({
            'id': doc.id,
            'nombre': doc.nombre,
            'url': doc.archivo.url,
            'fecha_subida': doc.fecha_subida.strftime('%d/%m/%Y %H:%M')
        })
    return JsonResponse({'ok': True, 'documentos': docs})

@require_GET
@csrf_exempt
def listar_documentos_licitacion(request, licitacion_id):
    # Permitir si usuario autenticado o si operador_manual_id en sesión
    if not (request.user.is_authenticated or 'operador_manual_id' in request.session):
        return JsonResponse({'ok': False, 'error': 'No autorizado'}, status=403)
    licitacion = get_object_or_404(Licitacion, id=licitacion_id)
    # Documentos directos
    docs_licitacion = [
        {
            'id': doc.id,
            'nombre': doc.nombre,
            'url': doc.archivo.url,
            'fecha_subida': timezone.localtime(doc.fecha_subida).strftime('%d/%m/%Y %H:%M'),
            'origen': 'licitacion',
        }
        for doc in licitacion.documentos.all().order_by('-fecha_subida')
    ]
    # Documentos de bitácora
    docs_bitacora = []
    for bitacora in licitacion.bitacoras.all():
        for doc in getattr(bitacora, 'archivos', []).all():
            docs_bitacora.append({
                'id': doc.id,
                'nombre': doc.nombre,
                'url': doc.archivo.url,
                'fecha_subida': timezone.localtime(doc.fecha_subida).strftime('%d/%m/%Y %H:%M'),
                'origen': 'bitacora',
                'bitacora_id': bitacora.id,
                'bitacora_texto': bitacora.texto,
                'bitacora_fecha': timezone.localtime(bitacora.fecha).strftime('%d/%m/%Y %H:%M'),
            })    # Unir ambos, pero eliminar duplicados basados en el nombre del archivo
    # Primero convertimos a un diccionario para eliminar duplicados por nombre
    docs_dict = {}
    
    # Agregar documentos de licitación primero (tienen prioridad)
    for doc in docs_licitacion:
        key = doc['nombre'].lower().strip()  # Clave normalizada
        docs_dict[key] = doc
    
    # Agregar documentos de bitácora solo si no existen ya
    for doc in docs_bitacora:
        key = doc['nombre'].lower().strip()  # Clave normalizada
        if key not in docs_dict:
            docs_dict[key] = doc
    
    # Convertir de vuelta a lista
    docs = list(docs_dict.values())
    
    # Ordenar por fecha_subida descendente
    docs.sort(key=lambda d: d['fecha_subida'], reverse=True)
    
    # Verificar si hay licitación fallida vinculada
    licitacion_fallida_data = None
    if hasattr(licitacion, 'licitacion_fallida_linkeada') and licitacion.licitacion_fallida_linkeada:
        fallida = licitacion.licitacion_fallida_linkeada
        # Obtener la última entrada de bitácora de la licitación fallida
        ultima_bitacora = BitacoraLicitacion.objects.filter(licitacion=fallida).order_by('-fecha').first()
        
        operador_name = '-'
        if fallida.operador_user:
            operador_name = fallida.operador_user.get_full_name() or fallida.operador_user.username
        
        licitacion_fallida_data = {
            'id': fallida.id,
            'numero_pedido': fallida.numero_pedido,
            'iniciativa': fallida.iniciativa,
            'operador': operador_name,
            'etapa': fallida.etapa_fk.nombre if fallida.etapa_fk else '-',
            'fecha_creacion': timezone.localtime(fallida.fecha_creacion).strftime('%d/%m/%Y %H:%M') if fallida.fecha_creacion else '-',
            'fecha_fallo': timezone.localtime(ultima_bitacora.fecha).strftime('%d/%m/%Y %H:%M') if ultima_bitacora else '-',
            'url_bitacora': f"/bitacora/{fallida.id}/?from_documents=1&licitacion_id={licitacion.id}"
        }
    
    return JsonResponse({
        'ok': True, 
        'documentos': docs,
        'licitacion_fallida': licitacion_fallida_data
    })

# API para obtener la etapa actual de un proyecto
@require_GET
def etapa_actual_api(request, licitacion_id):
    licitacion = get_object_or_404(Licitacion, id=licitacion_id)
    return JsonResponse({
        'etapa_id': licitacion.etapa_fk.id if licitacion.etapa_fk else '',
        'etapa_nombre': licitacion.etapa_fk.nombre if licitacion.etapa_fk else ''
    })

def etapas_licitacion_api(request, licitacion_id):
    """
    API que devuelve las etapas de una licitación con información de inhabilitación
    """
    licitacion = get_object_or_404(Licitacion, id=licitacion_id)
    
    # Obtener todas las etapas con información de inhabilitación
    etapas_con_info = licitacion.get_etapas_todas_con_inhabilitacion()
    
    etapas_data = []
    for etapa_info in etapas_con_info:
        rel = etapa_info['rel']
        etapa = etapa_info['etapa']
        etapas_data.append({
            'id': etapa.id,
            'nombre': etapa.nombre,
            'orden': rel.orden,
            'inhabilitada': etapa_info['inhabilitada']
        })
    
    return JsonResponse({
        'etapas': etapas_data,
        'debe_saltar_consejo': licitacion.debe_saltar_aprobacion_consejo(),
        'moneda': licitacion.moneda.nombre if licitacion.moneda else None,
        'monto': float(licitacion.monto_presupuestado) if licitacion.monto_presupuestado else None
    })

@csrf_exempt
def eliminar_documento_licitacion(request, licitacion_id, doc_id):
    licitacion = get_object_or_404(Licitacion, id=licitacion_id)
    doc = get_object_or_404(DocumentoLicitacion, id=doc_id, licitacion=licitacion)
    doc.archivo.delete(save=False)
    doc.delete()
    return JsonResponse({'ok': True})

@require_POST
@csrf_exempt
def guardar_observacion_operador(request, licitacion_id):
    if not (request.user.is_authenticated or 'operador_manual_id' in request.session):
        return JsonResponse({'ok': False, 'error': 'No autorizado'}, status=403)
    licitacion = get_object_or_404(Licitacion, id=licitacion_id)
    comentario = request.POST.get('comentario')
    if comentario is None:
        comentario = request.POST.get('texto', '').strip()
    else:
        comentario = comentario.strip()
    avanzar_etapa = request.POST.get('avanzar_etapa') == 'true' or request.POST.get('avanzar_etapa') == 'on'
    retroceder_etapa = request.POST.get('retroceder_etapa') == 'true' or request.POST.get('retroceder_etapa') == 'on'
    
    # Verificar acción de etapa por el campo accion_etapa (para el formulario de bitácora)
    accion_etapa = request.POST.get('accion_etapa', 'none')
    if accion_etapa == 'advance':
        avanzar_etapa = True
    elif accion_etapa == 'retreat':
        retroceder_etapa = True
    
    archivos = request.FILES.getlist('archivos')
    operador_user = None
    if hasattr(request.user, 'perfil') and getattr(request.user.perfil, 'rol', None) == 'operador':
        operador_user = request.user
    elif 'operador_manual_id' in request.session:
        operador_user = User.objects.filter(id=request.session['operador_manual_id']).first()
    # Cambiar estado a 'fallido' si se marcó la casilla correspondiente
    marcar_fallida_val = request.POST.get('marcar_fallida')
    marcar_fallida = marcar_fallida_val in ['true', 'on', '1']
    tipo_fallida = request.POST.get('tipo_fallida', '').strip()
    
    # Validar que si se marca como fallida, se seleccione un tipo
    if marcar_fallida and not tipo_fallida:
        return JsonResponse({'ok': False, 'error': 'Debe seleccionar un tipo de falla.'}, status=400)
    
    # Validar que el tipo de falla sea válido si se proporciona
    if tipo_fallida and tipo_fallida not in ['revocada', 'anulada', 'desierta']:
        return JsonResponse({'ok': False, 'error': 'Tipo de falla no válido'}, status=400)
    
    if marcar_fallida:
        estado_fallido = Estado.objects.filter(nombre__icontains='fallid').first()
        if estado_fallido and licitacion.estado_fk != estado_fallido:
            licitacion.estado_fk = estado_fallido
            # Actualizar el tipo de falla si se proporciona
            if tipo_fallida:
                licitacion.tipo_fallida = tipo_fallida
            licitacion.save()
    if not comentario and not archivos:
        return JsonResponse({'ok': False, 'error': 'Debe ingresar un comentario o adjuntar archivos.'}, status=400)
    
    # Preparar el texto de la bitácora
    texto_bitacora = comentario if comentario else 'Archivo adjunto'
    if marcar_fallida and tipo_fallida:
        texto_bitacora += f"\n\n⚠️ LICITACIÓN MARCADA COMO FALLIDA ({tipo_fallida.upper()})"
    
    # Crear una sola observación de bitácora
    b = BitacoraLicitacion.objects.create(
        licitacion=licitacion,
        operador_user=operador_user,
        texto=texto_bitacora,
        etapa=licitacion.etapa_fk
    )
    from .models import DocumentoBitacora
    for archivo in archivos:
        DocumentoBitacora.objects.create(
            bitacora=b,
            archivo=archivo,
            nombre=archivo.name
        )
    nueva_etapa = None
    # Usar las etapas habilitadas (excluyendo aprobación del consejo si aplica)
    etapas_habilitadas = licitacion.get_etapas_habilitadas()
    etapas_tipo = [rel.etapa for rel in etapas_habilitadas]
    
    try:
        idx = [e.id for e in etapas_tipo].index(licitacion.etapa_fk.id)
        if avanzar_etapa and idx < len(etapas_tipo) - 1:
            nueva_etapa = etapas_tipo[idx + 1]
            licitacion.etapa_fk = nueva_etapa
            licitacion.save()
            BitacoraLicitacion.objects.create(
                licitacion=licitacion,
                operador_user=operador_user,
                texto=f"Avance automático de etapa: {nueva_etapa.nombre}",
                etapa=nueva_etapa
            )
        elif retroceder_etapa and idx > 0:
            # Verificar si puede retroceder (solo si su última observación no avanzó etapa)
            ultima_bitacora = BitacoraLicitacion.objects.filter(
                licitacion=licitacion, 
                operador_user=operador_user
            ).order_by('-fecha').first()
            
            puede_retroceder = True
            if ultima_bitacora:
                texto_lower = ultima_bitacora.texto.lower()
                if 'avance automático de etapa' in texto_lower or 'avanzar etapa' in texto_lower:
                    puede_retroceder = False
            
            if not puede_retroceder:
                return JsonResponse({'ok': False, 'error': 'No puede retroceder etapa porque su última observación avanzó etapa.'}, status=400)
            
            nueva_etapa = etapas_tipo[idx - 1]
            licitacion.etapa_fk = nueva_etapa
            licitacion.save()
            BitacoraLicitacion.objects.create(
                licitacion=licitacion,
                operador_user=operador_user,
                texto=f"Retroceso automático de etapa: {nueva_etapa.nombre}",
                etapa=nueva_etapa
            )
    except Exception:
        pass
    return JsonResponse({'ok': True, 'cambio_etapa': bool(nueva_etapa)})

@csrf_exempt
def cerrar_licitacion_operador(request, licitacion_id):
    """
    Vista para cerrar una licitación desde la vista de operador.
    Cambia el estado a "CERRADA" (ID 3) y registra en la bitácora.
    """
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'Método no permitido'}, status=405)
    
    # Verificar autenticación
    if not (request.user.is_authenticated or 'operador_manual_id' in request.session):
        return JsonResponse({'ok': False, 'error': 'No autorizado'}, status=403)
    
    # Obtener la licitación
    licitacion = get_object_or_404(Licitacion, id=licitacion_id)
    
    # Verificar que la licitación no esté ya cerrada
    estado_cerrada = Estado.objects.filter(id=3).first()  # Estado "CERRADA" con ID 3
    if not estado_cerrada:
        return JsonResponse({'ok': False, 'error': 'Estado CERRADA no encontrado en la base de datos'}, status=500)
    
    if licitacion.estado_fk and licitacion.estado_fk.id == 3:
        return JsonResponse({'ok': False, 'error': 'La licitación ya está cerrada'}, status=400)
    
    # Obtener los datos del formulario
    motivo_cierre = request.POST.get('texto', '').strip()
    licitacion_fallida = request.POST.get('licitacion_fallida') in ['true', 'on', '1']
    tipo_fallida = request.POST.get('tipo_fallida', '').strip()
    
    # Validar que se haya ingresado un motivo
    if not motivo_cierre:
        return JsonResponse({'ok': False, 'error': 'Debe especificar el motivo del cierre'}, status=400)
    
    # Validar que si está marcada como fallida, se haya seleccionado un tipo
    if licitacion_fallida and not tipo_fallida:
        return JsonResponse({'ok': False, 'error': 'Debe seleccionar el tipo de falla para una licitación fallida'}, status=400)
    
    # Validar que el tipo de falla sea válido si se proporciona
    if tipo_fallida and tipo_fallida not in ['revocada', 'anulada', 'desierta']:
        return JsonResponse({'ok': False, 'error': 'Tipo de falla no válido'}, status=400)
    
    # Obtener el operador
    operador_user = None
    if hasattr(request.user, 'perfil') and getattr(request.user.perfil, 'rol', None) == 'operador':
        operador_user = request.user
    elif 'operador_manual_id' in request.session:
        operador_user = User.objects.filter(id=request.session['operador_manual_id']).first()
    
    try:
        # Construir el texto para la bitácora
        texto_bitacora = f"🔒 LICITACIÓN CERRADA\n\nMotivo: {motivo_cierre}"
        
        if licitacion_fallida:
            texto_bitacora += f"\n\nEstado adicional:\n- Licitación fue FALLIDA ({tipo_fallida.upper()})"
        
        # Actualizar el campo tipo_fallida si es necesario
        if licitacion_fallida and tipo_fallida:
            licitacion.tipo_fallida = tipo_fallida
        
        # Cambiar el estado de la licitación a "CERRADA"
        licitacion.estado_fk = estado_cerrada
        licitacion.save()
        
        # Registrar en la bitácora
        BitacoraLicitacion.objects.create(
            licitacion=licitacion,
            operador_user=operador_user,
            texto=texto_bitacora,
            etapa=licitacion.etapa_fk
        )
        
        return JsonResponse({
            'ok': True, 
            'mensaje': 'Licitación cerrada correctamente',
            'nuevo_estado': estado_cerrada.nombre
        })
        
    except Exception as e:
        return JsonResponse({'ok': False, 'error': f'Error al cerrar la licitación: {str(e)}'}, status=500)

@login_required
@require_http_methods(["GET", "POST", "DELETE"])
@csrf_exempt
def observacion_bitacora_api(request, bitacora_id):
    bitacora = get_object_or_404(BitacoraLicitacion, id=bitacora_id)
    if request.method == 'GET':
        obs = getattr(bitacora, 'observacion', None)
        if obs:
            return JsonResponse({'ok': True, 'texto': obs.texto})
        return JsonResponse({'ok': False, 'error': 'Sin observación'})
    elif request.method == 'POST':
        import json
        data = json.loads(request.body)
        texto = data.get('texto', '').strip()
        if not texto:
            return JsonResponse({'ok': False, 'error': 'Texto vacío'})
        obs, created = ObservacionBitacora.objects.get_or_create(bitacora=bitacora)
        obs.texto = texto
        obs.save()
        return JsonResponse({'ok': True})
    elif request.method == 'DELETE':
        obs = getattr(bitacora, 'observacion', None)
        if obs:
            obs.delete()
            return JsonResponse({'ok': True})
        return JsonResponse({'ok': False, 'error': 'No existe observación'})
    return JsonResponse({'ok': False, 'error': 'Método no permitido'}, status=405)

@csrf_exempt
def agregar_proyecto(request):
    try:
        data = json.loads(request.body)
        numero_pedido = data.get('numero_pedido')
        if not numero_pedido:
            return JsonResponse({'ok': False, 'error': 'El N° de pedido es obligatorio.'}, status=400)
        if Licitacion.objects.filter(numero_pedido=numero_pedido).exists():
            return JsonResponse({'ok': False, 'error': 'No se puede guardar una licitación con un N° de pedido repetido.'}, status=400)        # Obtener el estado "En curso" (o el que corresponda)
        estado_en_curso = Estado.objects.filter(nombre__iexact='en curso').first()        # Convertir el monto a número de forma segura
        try:
            monto_presupuestado = float(data.get('monto_presupuestado') or 0)
        except (ValueError, TypeError):
            monto_presupuestado = 0
        #tipo_presupuesto = get_tipo_presupuesto(Moneda.objects.get(id=data.get('moneda')) if data.get('moneda') else None, monto_presupuestado)
        tipo_presupuesto = data.get('tipo_presupuesto')
        
        # Crear la licitación
        licitacion = Licitacion(
            numero_pedido=numero_pedido,
            id_mercado_publico=data.get('id_mercado_publico', ''),
            numero_cuenta=data.get('numero_cuenta', ''),
            operador_user=User.objects.get(id=data.get('operador')) if data.get('operador') else None,
            operador_2=User.objects.get(id=data.get('operador_2')) if data.get('operador_2') else None,
            tipo_licitacion=TipoLicitacion.objects.get(id=data.get('tipo_licitacion')) if data.get('tipo_licitacion') else None,
            moneda=Moneda.objects.get(id=data.get('moneda')) if data.get('moneda') else None,
            categoria=Categoria.objects.get(id=data.get('categoria')) if data.get('categoria') else None,
            en_plan_anual=data.get('en_plan_anual', False),
            iniciativa=data.get('iniciativa', ''),
            direccion=data.get('direccion', ''),
            institucion=data.get('institucion', ''),
            etapa_fk=Etapa.objects.get(id=data.get('etapa')) if data.get('etapa') else None,
            departamento=Departamento.objects.get(id=data.get('departamento')) if data.get('departamento') else None,
            monto_presupuestado=monto_presupuestado,
            llamado_cotizacion=data.get('llamado_cotizacion', ''),
            tipo_presupuesto=tipo_presupuesto,
            estado_fk=estado_en_curso,
            pedido_devuelto=data.get('pedido_devuelto', False),            # Agregar la licitación fallida si se proporcionó un ID
            licitacion_fallida_linkeada=Licitacion.objects.get(id=data.get('licitacion_fallida_linkeada')) if data.get('licitacion_fallida_linkeada') else None
        )
        licitacion.save()
          # Asignar financiamiento (ManyToMany)
        financiamiento_ids = data.get('financiamiento')
        if financiamiento_ids:
            if not isinstance(financiamiento_ids, list):
                financiamiento_ids = [financiamiento_ids]
            licitacion.financiamiento.set(financiamiento_ids)
        
        # Crear entrada en bitácora si se linkeó una licitación fallida
        if licitacion.licitacion_fallida_linkeada:
            fallida = licitacion.licitacion_fallida_linkeada
            texto_linkeo = f"Esta licitación ha sido vinculada con la licitación fallida N° {fallida.numero_pedido} - '{fallida.iniciativa}' (ID: {fallida.id})"
            
            BitacoraLicitacion.objects.create(
                licitacion=licitacion,
                texto=texto_linkeo,
                etapa=licitacion.etapa_fk
            )
            
        return JsonResponse({'ok': True, 'id': licitacion.id})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)

@require_POST
def eliminar_bitacora(request, bitacora_id):
    from .models import BitacoraLicitacion
    bitacora = get_object_or_404(BitacoraLicitacion, id=bitacora_id)
    bitacora.delete()
    return JsonResponse({'ok': True})

@require_GET
@login_required
def exportar_licitacion_excel(request, licitacion_id):
    """
    Exporta la licitación y/o su bitácora a Excel según el parámetro 'tipo'.
    tipo=licitacion | bitacora | ambos
    """
    tipo = request.GET.get('tipo', 'licitacion')
    licitacion = get_object_or_404(Licitacion, id=licitacion_id)
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')

    # Create workbook and header format
    workbook = writer.book
    header_format = workbook.add_format({'bold': True, 'text_wrap': True, 'valign': 'top', 'fg_color': '#D7E4BC', 'border': 1})

    # Datos de la licitación
    if tipo in ['licitacion', 'ambos']:
        lic_data = {
            'ID': [licitacion.id],
            'N° Pedido': [licitacion.numero_pedido],
            'ID Mercado Público': [licitacion.id_mercado_publico or '-'],
            'N° Cuenta': [licitacion.numero_cuenta],
            'Profesional a Cargo': [licitacion.operador_user.get_full_name() if licitacion.operador_user else licitacion.operador_user.username if licitacion.operador_user else ''],
            'Tipo Licitación': [str(licitacion.tipo_licitacion) if licitacion.tipo_licitacion else ''],
            'Moneda': [str(licitacion.moneda) if licitacion.moneda else ''],
            'Categoría': [str(licitacion.categoria) if licitacion.categoria else ''],
            'Financiamiento': [', '.join([str(f) for f in licitacion.financiamiento.all()])],
            'En plan anual': ['Sí' if licitacion.en_plan_anual else 'No'],
            'Pedido devuelto': ['Sí' if licitacion.pedido_devuelto else 'No'],
            'Iniciativa': [licitacion.iniciativa],
            'Dirección': [licitacion.direccion or ''],
            'Institución': [licitacion.institucion or ''],
            'Etapa': [str(licitacion.etapa_fk) if licitacion.etapa_fk else ''],
            'Estado': [str(licitacion.estado_fk) if licitacion.estado_fk else ''],
            'Departamento': [licitacion.departamento],
            'Monto Presupuestado': [licitacion.monto_presupuestado],
            'Llamado Cotización': [licitacion.get_llamado_cotizacion_display() or ''],
            'Fecha de creación': [licitacion.fecha_creacion.strftime('%d/%m/%Y %H:%M') if licitacion.fecha_creacion else ''],
        }
        df_licit = pd.DataFrame(lic_data)
        df_licit.to_excel(writer, sheet_name='Licitacion', index=False)

        # Adjust column widths and formatting
        worksheet = writer.sheets['Licitacion']
        for i, column in enumerate(df_licit.columns):
            column_width = max(df_licit[column].astype(str).map(len).max(), len(column)) + 2
            worksheet.set_column(i, i, column_width)
        for col_num, value in enumerate(df_licit.columns.values):
            worksheet.write(0, col_num, value, header_format)

    # Bitácora
    if tipo in ['bitacora', 'ambos']:
        bitacoras = licitacion.bitacoras.all().order_by('fecha')
        bitacora_data = []
        for b in bitacoras:
            bitacora_data.append({
                'Fecha': b.fecha.strftime('%d/%m/%Y %H:%M'),
                'Etapa': str(b.etapa) if b.etapa else '',
                'Operador': str(b.operador_user) if b.operador_user else '',
                'Texto': b.texto,
                'Archivos': ', '.join([doc.nombre for doc in getattr(b, 'archivos', []).all()])
            })
        df_bit = pd.DataFrame(bitacora_data)
        df_bit.to_excel(writer, sheet_name='Bitacora', index=False)

        # Adjust column widths and formatting
        worksheet = writer.sheets['Bitacora']
        for i, column in enumerate(df_bit.columns):
            column_width = max(df_bit[column].astype(str).map(len).max(), len(column)) + 2
            worksheet.set_column(i, i, column_width)
        for col_num, value in enumerate(df_bit.columns.values):
            worksheet.write(0, col_num, value, header_format)

    writer.close()
    output.seek(0)
    filename = f"licitacion_{licitacion.numero_pedido}_export.xlsx"
    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename={filename}'
    return response

@require_GET
@login_required
def exportar_todas_licitaciones_excel(request):
    """
    Exporta todas las licitaciones a un archivo Excel.
    """
    try:
        # Obtenemos todas las licitaciones (o aplicamos filtros si existen en request.GET)
        q = request.GET.get('q')
        solo_anuales = request.GET.get('solo_anuales') == '1'
        solo_fallidas = request.GET.get('solo_fallidas') == '1'
        
        licitaciones = Licitacion.objects.all()
        
        if q:
            licitaciones = licitaciones.filter(
                models.Q(numero_pedido__icontains=q) | 
                models.Q(iniciativa__icontains=q)
            )
        
        if solo_anuales:
            licitaciones = licitaciones.filter(en_plan_anual=True)
        
        if solo_fallidas:
            # Buscar estados que puedan indicar "fallido" con diferentes variaciones
            estado_fallido = Estado.objects.filter(
                models.Q(nombre__iexact='fallido') | 
                models.Q(nombre__iexact='fallida') | 
                models.Q(nombre__icontains='fallid')
            ).first()
            if estado_fallido:
                licitaciones = licitaciones.filter(estado_fk=estado_fallido)
        
        # Ordenar las licitaciones
        licitaciones = licitaciones.order_by('-fecha_creacion')
        
        # Crear el archivo Excel
        output = io.BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        
        # Configuración del libro y formato del encabezado
        workbook = writer.book
        header_format = workbook.add_format({
            'bold': True, 
            'text_wrap': True, 
            'valign': 'top', 
            'fg_color': '#D7E4BC', 
            'border': 1
        })
        
        # Datos de todas las licitaciones
        licitaciones_data = []
        
        for licitacion in licitaciones:
            licitaciones_data.append({
                'ID': licitacion.id,
                'N° Pedido': licitacion.numero_pedido,
                'ID Mercado Público': licitacion.id_mercado_publico or '-',
                'N° Cuenta': licitacion.numero_cuenta,
                'Profesional a Cargo': licitacion.operador_user.get_full_name() if licitacion.operador_user else licitacion.operador_user.username if licitacion.operador_user else '',
                'Tipo Licitación': str(licitacion.tipo_licitacion) if licitacion.tipo_licitacion else '',
                'Moneda': str(licitacion.moneda) if licitacion.moneda else '',
                'Categoría': str(licitacion.categoria) if licitacion.categoria else '',
                'Financiamiento': ', '.join([str(f) for f in licitacion.financiamiento.all()]),
                'En plan anual': 'Sí' if licitacion.en_plan_anual else 'No',
                'Pedido devuelto': 'Sí' if licitacion.pedido_devuelto else 'No',
                'Iniciativa': licitacion.iniciativa,
                'Dirección': licitacion.direccion or '',
                'Institución': licitacion.institucion or '',
                'Etapa': str(licitacion.etapa_fk) if licitacion.etapa_fk else '',
                'Estado': str(licitacion.estado_fk) if licitacion.estado_fk else '',
                'Departamento': str(licitacion.departamento) if licitacion.departamento else '',
                'Monto Presupuestado': licitacion.monto_presupuestado,
                'Llamado Cotización': licitacion.get_llamado_cotizacion_display() or '',
                'Fecha de creación': licitacion.fecha_creacion.strftime('%d/%m/%Y %H:%M') if licitacion.fecha_creacion else '',
            })
        
        # Crear DataFrame y exportar a Excel
        df_licit = pd.DataFrame(licitaciones_data)
        df_licit.to_excel(writer, sheet_name='Licitaciones', index=False)
        
        # Ajustar anchos de columna y formato
        worksheet = writer.sheets['Licitaciones']
        for i, column in enumerate(df_licit.columns):
            column_width = max(df_licit[column].astype(str).map(len).max(), len(column)) + 2
            worksheet.set_column(i, i, column_width)
        for col_num, value in enumerate(df_licit.columns.values):
            worksheet.write(0, col_num, value, header_format)
        
        writer.close()
        output.seek(0)
        
        # Generar nombre del archivo con fecha actual y filtros aplicados
        fecha_actual = timezone.localtime(timezone.now()).strftime('%Y-%m-%d')
        filename_parts = ["licitaciones"]
        
        if solo_anuales:
            filename_parts.append("anuales")
        if solo_fallidas:
            filename_parts.append("fallidas")
            
        filename_parts.append(fecha_actual)
        filename = "_".join(filename_parts) + ".xlsx"
        
        # Enviar respuesta HTTP
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
    except Exception as e:
        # En caso de error, mostrar un mensaje de error
        return HttpResponse(f"Error al exportar las licitaciones: {str(e)}", status=500)

@require_GET
def api_validar_numero_pedido(request):
    numero_pedido = request.GET.get('numero_pedido')
    excluir_id = request.GET.get('excluir_id')
    qs = Licitacion.objects.filter(numero_pedido=numero_pedido)
    if excluir_id:
        qs = qs.exclude(id=excluir_id)
    exists = qs.exists()
    return JsonResponse({'exists': exists})

@csrf_exempt
@require_GET
def api_ultima_observacion(request, licitacion_id):
    # Solo operadores pueden acceder
    if not (request.user.is_authenticated or 'operador_manual_id' in request.session or 'operador_id' in request.session):
        return JsonResponse({'ok': False, 'error': 'No autorizado'}, status=403)
    licitacion = Licitacion.objects.filter(id=licitacion_id).first()
    if not licitacion:
        return JsonResponse({'ok': False, 'error': 'Licitación no encontrada'}, status=404)
    
    # Buscar la última observación hecha por el operador
    ultima_operador = BitacoraLicitacion.objects.filter(licitacion=licitacion, operador_user__isnull=False).order_by('-fecha').first()
    
    operador_data = {
        'texto': ultima_operador.texto if ultima_operador else '',
        'fecha': ultima_operador.fecha.strftime('%d/%m/%Y %H:%M') if ultima_operador and ultima_operador.fecha else '',
        'archivos': []
    }
    
    if ultima_operador:
        operador_data['archivos'] = [
            {
                'nombre': doc.nombre or doc.archivo.name.split('/')[-1],
                'url': doc.archivo.url
            }
            for doc in ultima_operador.archivos.all()
        ]
    
    # Buscar la última observación del administrador (a través de ObservacionBitacora)
    ultima_admin = None
    admin_data = {
        'texto': '',
        'fecha': ''
    }
    
    # Primero, buscar la última bitácora que tenga una observación asociada
    bitacora_con_obs = BitacoraLicitacion.objects.filter(
        licitacion=licitacion,
        observacion__isnull=False
    ).order_by('-fecha').first()
    
    if bitacora_con_obs:
        try:
            observacion_admin = bitacora_con_obs.observacion;
            admin_data = {
                'texto': observacion_admin.texto,
                'fecha': observacion_admin.fecha.strftime('%d/%m/%Y %H:%M') if observacion_admin.fecha else ''
            }
        except:
            pass
            
    return JsonResponse({
        'ok': True, 
        'operador': operador_data,
        'admin': admin_data
    })

@require_GET
def api_licitaciones_fallidas(request):
    """
    API para obtener listado de licitaciones con estado fallido
    """
    # Verificar permisos
    if not (request.user.is_authenticated or 'operador_manual_id' in request.session or 'operador_id' in request.session):
        return JsonResponse({'ok': False, 'error': 'No autorizado'}, status=403)
    
    # Obtener todas las licitaciones con estado "fallido"
    estado_fallido = Estado.objects.filter(nombre__icontains='fallid').first()
    
    if not estado_fallido:
        return JsonResponse({'ok': False, 'error': 'No se encontró un estado que coincida con "fallido"'}, status=404)    # Obtener licitaciones fallidas
    licitaciones = Licitacion.objects.select_related('operador_user', 'etapa_fk').filter(estado_fk=estado_fallido).order_by('-id')
    
    # Convertir a formato JSON
    licitaciones_data = []
    for licitacion in licitaciones:
        # Intentar encontrar la entrada de bitácora que marca la licitación como fallida
        # Primero buscamos en el texto alguna referencia a "fallida"
        entrada_fallida = BitacoraLicitacion.objects.filter(
            licitacion=licitacion,
            texto__icontains='fallid'  # Esto buscará "fallido", "fallida", etc.
        ).order_by('-fecha').first()
        
        # Si no encontramos entrada con texto relacionado a "fallida", tomamos la última entrada
        if not entrada_fallida:
            entrada_fallida = BitacoraLicitacion.objects.filter(
                licitacion=licitacion
            ).order_by('-fecha').first()
        
        fecha_fallo = entrada_fallida.fecha.strftime('%d/%m/%Y %H:%M') if entrada_fallida and entrada_fallida.fecha else '-'
        fecha_creacion = licitacion.fecha_creacion.strftime('%d/%m/%Y %H:%M') if licitacion.fecha_creacion else '-'
        
        operador_name = '-'
        if licitacion.operador_user:
            operador_name = licitacion.operador_user.get_full_name() or licitacion.operador_user.username
        
        licitaciones_data.append({
            'id': licitacion.id,
            'numero_pedido': licitacion.numero_pedido,
            'iniciativa': licitacion.iniciativa,
            'operador_nombre': operador_name,
            'etapa_nombre': licitacion.etapa_fk.nombre if licitacion.etapa_fk else '-',
            'fecha_creacion': fecha_creacion,
            'fecha_fallo': fecha_fallo
        })
    return JsonResponse({
        'ok': True,
        'licitaciones': licitaciones_data
    })

@csrf_exempt
def api_linkear_licitacion_fallida(request):
    """
    API para linkear una licitación fallida a una nueva licitación
    Método POST
    Parámetros:
    - licitacion_id: ID de la licitación nueva
    - licitacion_fallida_id: ID de la licitación fallida a linkear
    """
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'Método no soportado'}, status=405)
    
    # Verificar permisos
    if not (request.user.is_authenticated or 'operador_manual_id' in request.session or 'operador_id' in request.session):
        return JsonResponse({'ok': False, 'error': 'No autorizado'}, status=403)
    
    try:
        data = json.loads(request.body)
        licitacion_id = data.get('licitacion_id')
        licitacion_fallida_id = data.get('licitacion_fallida_id')
        
        if not licitacion_id or not licitacion_fallida_id:
            return JsonResponse({'ok': False, 'error': 'Faltan parámetros requeridos'}, status=400)
        
        # Obtener la licitación
        try:
            licitacion = Licitacion.objects.get(id=licitacion_id)
        except Licitacion.DoesNotExist:
            return JsonResponse({'ok': False, 'error': 'La licitación no existe'}, status=404)
        
        # Obtener la licitación fallida
        try:
            licitacion_fallida = Licitacion.objects.get(id=licitacion_fallida_id)
        except Licitacion.DoesNotExist:
            return JsonResponse({'ok': False, 'error': 'La licitación fallida no existe'}, status=404)
        
        # Linkear la licitación fallida
        licitacion.licitacion_fallida_linkeada = licitacion_fallida
        licitacion.save()
        
        # Crear entrada en bitácora cuando se linkea una licitación fallida
        texto_linkeo = f"Esta licitación ha sido vinculada con la licitación fallida N° {licitacion_fallida.numero_pedido} - '{licitacion_fallida.iniciativa}' (ID: {licitacion_fallida.id})"
        
        BitacoraLicitacion.objects.create(
            licitacion=licitacion,
            texto=texto_linkeo,
            etapa=licitacion.etapa_fk
        )
        
        return JsonResponse({
            'ok': True,
            'mensaje': 'Licitación fallida vinculada correctamente',
            'licitacion_id': licitacion.id,
            'licitacion_fallida_id': licitacion_fallida.id
        })
        
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)

@csrf_exempt
def actualizar_etapa_api(request, licitacion_id):
    """
    Endpoint AJAX para actualizar la etapa de una licitación.
    Espera POST con {etapa_id, accion, crear_entrada_bitacora} y retorna JSON con el nombre de la nueva etapa.
    """
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'Método no permitido'}, status=405)
    try:
        data = json.loads(request.body)
        etapa_id = data.get('etapa_id')
        accion = data.get('accion', 'cambio')  # 'avanzar', 'retroceder', o 'cambio'
        crear_entrada_bitacora = data.get('crear_entrada_bitacora', False)
        
        if not etapa_id:
            return JsonResponse({'ok': False, 'error': 'Falta etapa_id'}, status=400)
            
        licitacion = Licitacion.objects.get(id=licitacion_id)
        etapa_anterior = licitacion.etapa_fk
        nueva_etapa = Etapa.objects.get(id=etapa_id)
        
        # Verificar que la etapa a la que se quiere cambiar esté habilitada
        etapas_habilitadas = licitacion.get_etapas_habilitadas()
        etapas_habilitadas_ids = [rel.etapa.id for rel in etapas_habilitadas]
        
        if nueva_etapa.id not in etapas_habilitadas_ids:
            return JsonResponse({
                'ok': False, 
                'error': f'La etapa "{nueva_etapa.nombre}" está inhabilitada para esta licitación (UF < 500)'
            }, status=400)
        
        # Actualizar la etapa
        licitacion.etapa_fk = nueva_etapa
        licitacion.save()
        
        # Obtener información del operador activo después del cambio
        operador_activo = licitacion.get_operador_activo()
        numero_operador_activo = licitacion.get_numero_operador_activo()
        
        entrada_creada = False
        
        # Crear entrada automática en la bitácora si se solicita
        if crear_entrada_bitacora:
            from .models import BitacoraLicitacion
            
            # Determinar el texto del comentario según la acción
            if accion == 'avanzar':
                texto_comentario = f"🚀 Etapa avanzada automáticamente"
            elif accion == 'retroceder':
                texto_comentario = f"⬅️ Etapa retrocedida automáticamente"
            else:
                texto_comentario = f"🔄 Etapa modificada automáticamente"
            
            # Agregar información sobre el cambio
            if etapa_anterior:
                texto_comentario += f" de '{etapa_anterior.nombre}' a '{nueva_etapa.nombre}'"
            else:
                texto_comentario += f" a '{nueva_etapa.nombre}'"
            
            texto_comentario += f" desde el modal de cronología."
            
            # Obtener el operador actual (admin que realiza el cambio)
            operador_user = None
            if hasattr(request, 'user') and request.user.is_authenticated:
                operador_user = request.user
            
            
            # Crear la entrada en la bitácora
            BitacoraLicitacion.objects.create(
                licitacion=licitacion,
                operador_user=operador_user,
                texto=texto_comentario,
                etapa=nueva_etapa
            )
            entrada_creada = True
        
        return JsonResponse({
            'ok': True, 
            'etapa': {'id': nueva_etapa.id, 'nombre': nueva_etapa.nombre},
            'operador_activo': {
                'id': operador_activo.id if operador_activo else None,
                'nombre': operador_activo.get_full_name() if operador_activo else None,
                'username': operador_activo.username if operador_activo else None,
                'numero': numero_operador_activo
            },
            'entrada_bitacora_creada': entrada_creada
        })
        
    except Licitacion.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Licitación no encontrada'}, status=404)
    except Etapa.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Etapa no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)

@login_required
@require_GET
def obtener_notificaciones_api(request):
    """Obtener notificaciones no leídas para el admin"""
    perfil = getattr(request.user, 'perfil', None)
    if not perfil or perfil.rol != 'admin':
        return JsonResponse({'ok': False, 'error': 'Acceso denegado'}, status=403)
    
    # Obtener las últimas 10 notificaciones no leídas
    from .models import Notificacion
    notificaciones = Notificacion.objects.filter(leida=False).order_by('-fecha')[:10]
    
    data = []
    for notif in notificaciones:
        operador_name = notif.operador_user.get_full_name() if notif.operador_user else None
        if not operador_name and notif.operador_user:
            operador_name = notif.operador_user.username
            
        data.append({
            'id': notif.id,
            'tipo': notif.tipo,
            'titulo': notif.titulo,
            'mensaje': notif.mensaje,
            'licitacion_id': notif.licitacion.id if notif.licitacion else None,
            'licitacion_numero': notif.licitacion.numero_pedido if notif.licitacion else None,
            'operador': operador_name,
            'fecha': notif.fecha.strftime('%d/%m/%Y %H:%M'),
            'fecha_relativa': tiempo_relativo(notif.fecha)
        })
    
    total_no_leidas = Notificacion.objects.filter(leida=False).count()
    
    return JsonResponse({
        'ok': True,
        'notificaciones': data,
        'total_no_leidas': total_no_leidas
    })

@login_required
@csrf_exempt
def marcar_notificacion_leida(request, notificacion_id):
    """Marcar una notificación como leída"""
    perfil = getattr(request.user, 'perfil', None)
    if not perfil or perfil.rol != 'admin':
        return JsonResponse({'ok': False, 'error': 'Acceso denegado'}, status=403)
    
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'Método no permitido'}, status=405)

    
    try:
        from .models import Notificacion
        notificacion = Notificacion.objects.get(id=notificacion_id)
        notificacion.leida = True
        notificacion.save()
        
        return JsonResponse({'ok': True})
    except Notificacion.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Notificación no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)

@login_required
@csrf_exempt
def marcar_todas_notificaciones_leidas(request):
    """Marcar todas las notificaciones como leídas"""
    perfil = getattr(request.user, 'perfil', None)
    if not perfil or perfil.rol != 'admin':
        return JsonResponse({'ok': False, 'error': 'Acceso denegado'}, status=403)
    
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'Método no permitido'}, status=405)
    
    try:
        from .models import Notificacion
        Notificacion.objects.filter(leida=False).update(leida=True)
        
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)

def tiempo_relativo(fecha):
    """Devuelve tiempo transcurrido en formato relativo"""
    from django.utils import timezone
    import datetime
    
    ahora = timezone.now()
    diferencia = ahora - fecha
    
    if diferencia.days > 0:
        return f"hace {diferencia.days} día{'s' if diferencia.days > 1 else ''}"
    elif diferencia.seconds >= 3600:
        horas = diferencia.seconds // 3600
        return f"hace {horas} hora{'s' if horas > 1 else ''}"
    elif diferencia.seconds >= 60:
        minutos = diferencia.seconds // 60
        return f"hace {minutos} minuto{'s' if minutos > 1 else ''}"
    else:
        return "hace unos segundos"

@login_required
def calendario_actividad(request):
    """Vista para mostrar el calendario de actividad"""
    # Verificar que sea admin
    perfil = getattr(request.user, 'perfil', None)
    if not perfil or perfil.rol != 'admin':
        return HttpResponseForbidden("Acceso denegado")
    
    # Obtener años disponibles para el filtro
    años_licitaciones = Licitacion.objects.dates('fecha_creacion', 'year')
    años_bitacoras = BitacoraLicitacion.objects.dates('fecha', 'year')
    
    años_disponibles = set()
    for fecha in años_licitaciones:
        años_disponibles.add(fecha.year)
    for fecha in años_bitacoras:
        años_disponibles.add(fecha.year)
    
    años_disponibles = sorted(list(años_disponibles), reverse=True)
    
    # Obtener notificaciones no leídas
    notificaciones_no_leidas = Notificacion.objects.filter(
        leida=False
    ).order_by('-fecha')[:50]
    
    contexto = {
        'es_admin': True,
        'años_disponibles': años_disponibles,
        'año_actual': timezone.now().year,
        'mes_actual': timezone.now().month,
        'notificaciones': notificaciones_no_leidas,
        'notificaciones_count': notificaciones_no_leidas.count(),
    }
    
    return render(request, 'licitaciones/calendario_actividad.html', contexto)

@require_GET
def obtener_eventos_calendario(request):
    """API para obtener eventos del calendario"""
    # Verificar que sea admin
    perfil = getattr(request.user, 'perfil', None)
    if not perfil or perfil.rol != 'admin':
        return JsonResponse({'ok': False, 'error': 'Acceso denegado'}, status=403)
    
    try:
        # Obtener parámetros de fecha
        año = request.GET.get('año', timezone.now().year)
        mes = request.GET.get('mes', None)
        
        año = int(año)
        if mes:
            mes = int(mes)
        
        eventos = []
        
        # 1. Eventos de creación de licitaciones
        # Obtener fechas de inicio y fin para el filtro en zona horaria local
        if mes:
            # Filtrar por año y mes específico
            fecha_inicio = timezone.make_aware(datetime(año, mes, 1))
            if mes == 12:
                fecha_fin = timezone.make_aware(datetime(año + 1, 1, 1))
            else:
                fecha_fin = timezone.make_aware(datetime(año, mes + 1, 1))

            licitaciones_query = Licitacion.objects.select_related('operador_user', 'tipo_licitacion').filter(
                fecha_creacion__gte=fecha_inicio,
                fecha_creacion__lt=fecha_fin
            )
        else:
            # Filtrar solo por año
            fecha_inicio = timezone.make_aware(datetime(año, 1, 1))
            fecha_fin = timezone.make_aware(datetime(año + 1, 1, 1))
            
            licitaciones_query = Licitacion.objects.select_related('operador_user', 'tipo_licitacion').filter(
                fecha_creacion__gte=fecha_inicio,
                fecha_creacion__lt=fecha_fin
            )
        
        for licitacion in licitaciones_query:
            # Convertir a zona horaria local
            fecha_local = timezone.localtime(licitacion.fecha_creacion)
            eventos.append({
                'tipo': 'creacion',
                'fecha': fecha_local.strftime('%Y-%m-%d'),
                'hora': fecha_local.strftime('%H:%M'),
                'titulo': f'Licitación creada: {licitacion.numero_pedido}',
                'descripcion': f'{licitacion.iniciativa or "Sin iniciativa"}',
                'operador': str(licitacion.operador_user) if licitacion.operador_user else 'Sin operador',
                'tipo_licitacion': str(licitacion.tipo_licitacion),
                'licitacion_id': licitacion.id,
                'color': '#28a745'  # Verde para creaciones
            })
        
        # 2. Eventos de observaciones/cambios de etapa
        # Aplicar el mismo filtro de fechas para bitácoras
        if mes:
            bitacoras_query = BitacoraLicitacion.objects.select_related(
                'licitacion', 'operador_user', 'etapa'
            ).filter(
                fecha__gte=fecha_inicio,
                fecha__lt=fecha_fin
            )
        else:
            bitacoras_query = BitacoraLicitacion.objects.select_related(
                'licitacion', 'operador_user', 'etapa'
            ).filter(
                fecha__gte=fecha_inicio,
                fecha__lt=fecha_fin
            )
        
        for bitacora in bitacoras_query:
            # Convertir a zona horaria local
            fecha_local = timezone.localtime(bitacora.fecha)
            
            # Determinar tipo de evento
            texto_lower = bitacora.texto.lower()
            if 'etapa' in texto_lower and ('cambió' in texto_lower or 'avanzó' in texto_lower or 'retrocedió' in texto_lower):
                tipo_evento = 'cambio_etapa'
                color = '#007bff'  # Azul para cambios de etapa
                icono = '📈'
            elif 'fallida' in texto_lower or 'cerrada' in texto_lower:
                tipo_evento = 'cierre'
                color = '#dc3545'  # Rojo para cierres
                icono = '❌'
            else:
                tipo_evento = 'observacion'
                color = '#ffc107'  # Amarillo para observaciones
                icono = '📝'
            
            eventos.append({
                'tipo': tipo_evento,
                'fecha': fecha_local.strftime('%Y-%m-%d'),
                'hora': fecha_local.strftime('%H:%M'),
                'titulo': f'{icono} Licitación {bitacora.licitacion.numero_pedido}',
                'descripcion': bitacora.texto[:100] + ('...' if len(bitacora.texto) > 100 else ''),
                'operador': str(bitacora.operador_user) if bitacora.operador_user else 'Sistema',
                'etapa': str(bitacora.etapa) if bitacora.etapa else 'Sin etapa',
                'licitacion_id': bitacora.licitacion.id,
                'bitacora_id': bitacora.id,
                'color': color
            })
        
        # Ordenar eventos por fecha y hora
        eventos.sort(key=lambda x: f"{x['fecha']} {x['hora']}", reverse=True)
        
        return JsonResponse({
            'ok': True,
            'eventos': eventos,
            'total': len(eventos)
        })
        
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)

@csrf_exempt
@require_GET
def api_puede_retroceder_etapa(request, licitacion_id):
    """
    API para verificar si el operador puede retroceder etapa.
    Solo puede retroceder si su última observación no avanzó etapa.
    """
    # Solo operadores pueden acceder
    if not (request.user.is_authenticated or 'operador_manual_id' in request.session or 'operador_id' in request.session):
        return JsonResponse({'ok': False, 'error': 'No autorizado'}, status=403)
    
    licitacion = Licitacion.objects.filter(id=licitacion_id).first()
    if not licitacion:
        return JsonResponse({'ok': False, 'error': 'Licitación no encontrada'}, status=404)
    
    # Obtener el operador actual
    operador_user = None
    if hasattr(request.user, 'perfil') and getattr(request.user.perfil, 'rol', None) == 'operador':
        operador_user = request.user
    elif 'operador_manual_id' in request.session:
        operador_user = User.objects.filter(id=request.session['operador_manual_id']).first()
    
    if not operador_user:
        return JsonResponse({'ok': False, 'puede_retroceder': False})
    
    # Buscar la última observación del operador para esta licitación
    ultima_bitacora = BitacoraLicitacion.objects.filter(
        licitacion=licitacion, 
        operador_user=operador_user
    ).order_by('-fecha').first()
    
    puede_retroceder = True
    
    if ultima_bitacora:
        # Verificar si el texto de la bitácora indica que avanzó etapa
        texto_lower = ultima_bitacora.texto.lower()
        if 'avance automático de etapa' in texto_lower or 'avanzar etapa' in texto_lower:
            puede_retroceder = False
    
    return JsonResponse({
        'ok': True, 
        'puede_retroceder': puede_retroceder,
        'razon': 'La última observación avanzó etapa' if not puede_retroceder else 'Puede retroceder'
    })
