from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, F
from django.utils import timezone
from datetime import timedelta

from customers.models import Customer, Motorcycle
from maintenance.models import MaintenanceOrder
from inventory.models import Product, StockMovement
from billing.models import Invoice, InvoiceItem

@login_required
def index(request):
    # Validar existencia de servicios base
    from inventory.services import ensure_default_services
    ensure_default_services()
    
    # 1. Métricas de Tarjetas
    total_customers = Customer.objects.count()
    total_motos = Motorcycle.objects.count()
    
    # Órdenes activas (no completadas ni entregadas)
    active_orders = MaintenanceOrder.objects.exclude(estado__in=['COMPLETADO', 'ENTREGADO']).count()
    
    # Ingresos (Ventas) del mes actual - Sin filtros de estado para depuración
    local_now = timezone.localtime(timezone.now())
    first_day_of_month = local_now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    monthly_revenue = Invoice.objects.filter(
        fecha__gte=first_day_of_month
    ).aggregate(total=Sum('total'))['total'] or 0

    # 2. Datos para Gráfica: Órdenes por Estado
    orders_by_status = list(MaintenanceOrder.objects.values('estado').annotate(count=Count('id')))
    
    # 3. Datos para Gráfica: Tendencia de Ventas vs Gastos (Últimos 7 días)
    # Calculamos el inicio del día hace 7 días (timezone aware para evitar problemas de DB)
    start_of_today = local_now.replace(hour=0, minute=0, second=0, microsecond=0)
    seven_days_ago_dt = start_of_today - timedelta(days=6)
    
    # Consultar Ingresos (Facturas) - Sin filtros de estado
    recent_invoices = Invoice.objects.filter(
        fecha__gte=seven_days_ago_dt
    )
    
    # Consultar Gastos (Entradas de Stock)
    recent_expenses = StockMovement.objects.filter(
        tipo='ENTRADA',
        fecha__gte=seven_days_ago_dt
    )

    income_map = {}
    for inv in recent_invoices:
        # Convertir a hora local para agrupar por el día correcto
        local_date = timezone.localtime(inv.fecha).date()
        date_str = local_date.strftime('%Y-%m-%d')
        income_map[date_str] = income_map.get(date_str, 0.0) + float(inv.total or 0)

    expense_map = {}
    for exp in recent_expenses:
        local_date = timezone.localtime(exp.fecha).date()
        date_str = local_date.strftime('%Y-%m-%d')
        total_exp = float((exp.cantidad or 0) * (exp.precio_compra_instante or 0))
        expense_map[date_str] = expense_map.get(date_str, 0.0) + total_exp

    revenue_trend = []

    for i in range(6, -1, -1):
        target_date = (local_now - timedelta(days=i)).date()
        target_date_str = target_date.strftime('%Y-%m-%d')
        
        revenue_trend.append({
            'day': target_date.strftime('%d/%m'),
            'income': str(income_map.get(target_date_str, 0.0)),
            'expense': str(expense_map.get(target_date_str, 0.0))
        })

    # 4. Top 5 Productos más vendidos (Excluyendo Servicios)
    top_products = InvoiceItem.objects.exclude(
        producto__categoria__nombre="SERVICIOS"
    ).values(
        'producto__nombre'
    ).annotate(
        total_sold=Sum('cantidad')
    ).order_by('-total_sold')[:5]

    # 5. Alertas de Inventario (Bajo stock) - Ignoramos categoría SERVICIOS
    inventory_alerts = Product.objects.filter(
        stock_actual__lte=F('stock_minimo'),
        is_active=True
    ).exclude(categoria__nombre="SERVICIOS").order_by('stock_actual')[:5]

    # 6. Actividad Reciente (Últimas 5 órdenes)
    recent_orders = MaintenanceOrder.objects.select_related('moto', 'moto__owner').order_by('-created_at')[:5]

    context = {
        'total_customers': total_customers,
        'total_motos': total_motos,
        'active_orders': active_orders,
        'monthly_revenue': monthly_revenue,
        'orders_by_status': orders_by_status,
        'revenue_trend': revenue_trend,
        'top_products': list(top_products),
        'inventory_alerts': inventory_alerts,
        'recent_orders': recent_orders,
    }

    print(context['revenue_trend'])

    return render(request, 'dashboard/index.html', context)
