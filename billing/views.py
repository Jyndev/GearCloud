from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from users.models import User
from .models import Invoice, InvoiceItem
from .services import crear_factura
from inventory.models import Product
from customers.models import Customer
from django.db.models import Sum
from django.contrib import messages
import json

@login_required
def billing_list(request):
    if request.user.role not in ['ADMIN', 'RECEPCION']:
        messages.error(request, "No tienes permiso para acceder al módulo de facturación.")
        return redirect('dashboard:index')

    from django.db.models.functions import TruncMonth
    from maintenance.models import MaintenanceOrder
    from django.utils import timezone
    import datetime

    facturas = Invoice.objects.select_related('cliente').all()
    
    total_aggregate = facturas.exclude(estado='ANULADA').aggregate(total=Sum('total'))['total']
    total_facturado = total_aggregate if total_aggregate else 0
    facturas_mes = facturas.filter(fecha__month=timezone.now().month).count() 
    
    # Datos para el gráfico (últimos 6 meses)
    seis_meses_atras = timezone.now() - datetime.timedelta(days=180)
    facturas_grafico = Invoice.objects.filter(
        estado='PAGADA', 
        fecha__gte=seis_meses_atras
    ).only('fecha', 'total')

    # Agrupar por mes en Python para evitar errores de zona horaria en MySQL
    chart_data_dict = {}
    meses_nombres = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    
    for f in facturas_grafico:
        # Clave del mes: "Año-Mes" para asegurar orden cronológico
        key = f.fecha.strftime('%Y-%m')
        if key not in chart_data_dict:
            chart_data_dict[key] = {'label': meses_nombres[f.fecha.month - 1], 'total': 0}
        chart_data_dict[key]['total'] += float(f.total)

    # Ordenar por la clave (año-mes) y separar en listas
    sorted_keys = sorted(chart_data_dict.keys())
    chart_labels = [chart_data_dict[k]['label'] for k in sorted_keys]
    chart_values = [chart_data_dict[k]['total'] for k in sorted_keys]

    # Obtener mecánicos para la liquidación
    mecanicos = User.objects.filter(role=User.ROLE_MECANICO)
    for mecanico in mecanicos:
        ordenes_mecanico = MaintenanceOrder.objects.filter(
            mecanico=mecanico,
            estado__in=['COMPLETADO', 'ENTREGADO'],
            comision_pagada=False # Solo órdenes no liquidadas
        )
        # Sumar solo la mano de obra para la comisión
        labor_total = ordenes_mecanico.aggregate(total=Sum('costo_mano_obra'))['total'] or 0
        mecanico.total_labor = labor_total
        mecanico.total_comision = (labor_total * mecanico.comision_porcentaje) / 100
        mecanico.count_ordenes = ordenes_mecanico.count()
    
    context = {
        'facturas': facturas,
        'total_facturado': total_facturado,
        'facturas_mes': facturas_mes,
        'mecanicos': mecanicos,
        'chart_labels': json.dumps(chart_labels),
        'chart_values': json.dumps(chart_values),
    }
    return render(request, 'billing/billing_list.html', context)

@login_required
def settle_commissions(request, user_id):
    if not request.user.is_admin():
        messages.error(request, "Solo administradores pueden liquidar comisiones.")
        return redirect('billing:billing_list')

    from maintenance.models import MaintenanceOrder
    mecanico = get_object_or_404(User, id=user_id, role=User.ROLE_MECANICO)
    
    ordenes = MaintenanceOrder.objects.filter(
        mecanico=mecanico,
        estado__in=['COMPLETADO', 'ENTREGADO'],
        comision_pagada=False
    )
    
    count = ordenes.count()
    if count > 0:
        ordenes.update(comision_pagada=True)
        messages.success(request, f"Se han liquidado {count} órdenes para el mecánico {mecanico.get_full_name() or mecanico.username}.")
    else:
        messages.warning(request, f"No hay órdenes pendientes de liquidar para este mecánico.")
        
    return redirect('billing:billing_list')

@login_required
def invoice_create(request):
    if request.user.role not in ['ADMIN', 'RECEPCION']:
        messages.error(request, "No tienes permiso para realizar ventas directas.")
        return redirect('dashboard:index')

    if request.method == 'POST':
        # Procesar los datos de la venta rápida (JSON desde el frontend)
        try:
            cliente_nombre = request.POST.get('cliente_nombre')
            items_json = request.POST.get('items_json')
            items_data = json.loads(items_json)
            
            crear_factura(items_data, cliente_nombre=cliente_nombre, user=request.user)
            messages.success(request, "Venta realizada con éxito.")
            return redirect('billing:billing_list')
        except Exception as e:
            messages.error(request, f"Error al procesar la venta: {str(e)}")
            return redirect('billing:invoice_create')

    # GET: Mostrar interfaz de venta rápida
    productos = Product.objects.filter(is_active=True, stock_actual__gt=0).select_related('categoria')
    
    context = {
        'productos': productos,
    }
    return render(request, 'billing/invoice_form.html', context)

@login_required
def invoice_detail(request, pk):
    if request.user.role not in ['ADMIN', 'RECEPCION']:
        messages.error(request, "No tienes permiso para ver detalles de facturación.")
        return redirect('dashboard:index')

    factura = get_object_or_404(Invoice, pk=pk)
    return render(request, 'billing/invoice_detail.html', {'factura': factura})

@login_required
def register_payment(request, pk):
    if request.user.role not in ['ADMIN', 'RECEPCION']:
        messages.error(request, "Solo el personal administrativo puede registrar pagos.")
        return redirect('dashboard:index')

    factura = get_object_or_404(Invoice, pk=pk)
    if request.method == 'POST':
        factura.estado = 'PAGADA'
        factura.save()
        
        # Si tiene una orden de mantenimiento asociada, marcarla como ENTREGADO
        if hasattr(factura, 'orden_mantenimiento'):
            orden = factura.orden_mantenimiento
            orden.estado = 'ENTREGADO'
            orden.save()
            messages.success(request, f"La factura {factura.consecutivo} ha sido PAGADA y la Orden {orden.codigo_ot} se ha marcado como ENTREGADA.")
        else:
            messages.success(request, f"La factura {factura.consecutivo} ha sido marcada como PAGADA.")
            
    return redirect('billing:invoice_detail', pk=pk)
