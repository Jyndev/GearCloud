from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Product, Supplier, Category, StockMovement
from .forms import ProductForm, SupplierForm, CategoryForm
from billing.models import Invoice, InvoiceItem
from django.db.models import Sum, F

@login_required
def inventory_list(request):
    # Validar existencia de servicios base (por si se borraron)
    from .services import ensure_default_services
    ensure_default_services()

    # Incluir todos los productos para permitir el filtrado dinámico en el cliente
    productos = Product.objects.select_related('categoria', 'proveedor').all()
    
    # Ventas reales basadas en facturación (excluyendo anuladas)
    facturas_validas = Invoice.objects.exclude(estado='ANULADA')
    items_vendidos = InvoiceItem.objects.filter(factura__in=facturas_validas)
    
    total_venta = facturas_validas.aggregate(total=Sum('total'))['total'] or 0
    
    # Calcular costo de lo vendido para obtener margen real
    # Como InvoiceItem no guarda el costo histórico, usamos el precio_compra actual del producto
    total_costo_vendido = sum(item.cantidad * item.producto.precio_compra for item in items_vendidos.select_related('producto'))
    
    margen = total_venta - total_costo_vendido
    
    # El valor del stock actual sigue siendo útil como referencia, lo renombramos internamente o mantenemos
    valor_stock_actual = sum(p.stock_actual * p.precio for p in productos)
    
    total_productos = productos.count()
    stock_bajo_count = sum(1 for p in productos if p.stock_bajo and p.categoria.nombre != 'SERVICIOS')
    proveedores_count = Product.objects.values('proveedor').distinct().count()
    
    context = {
        'productos': productos,
        'total_productos': total_productos,
        'stock_bajo_count': stock_bajo_count,
        'proveedores_count': proveedores_count,
        'costo_vendas': total_costo_vendido,
        'total_vendas': total_venta,
        'margen': margen,
        'valor_inventario': valor_stock_actual,
        'categorias': Category.objects.all(),
        'category_form': CategoryForm(),
        'product_form': ProductForm(),
    }
    return render(request, 'inventory/inventory_list.html', context)

@login_required
def stock_entry(request, pk):
    from django.shortcuts import get_object_or_404
    producto = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        cantidad = int(request.POST.get('cantidad', 0))
        p_compra = float(request.POST.get('precio_compra', producto.precio_compra))
        p_venta = float(request.POST.get('precio_venta', producto.precio))
        
        if cantidad > 0:
            producto.stock_actual += cantidad
            producto.precio_compra = p_compra
            producto.precio = p_venta
            producto.save()
            
            # Registrar Movimiento
            StockMovement.objects.create(
                producto=producto,
                tipo='ENTRADA',
                cantidad=cantidad,
                precio_compra_instante=p_compra,
                precio_venta_instante=p_venta,
                user=request.user,
                notas=f"Entrada manual de {cantidad} unidades"
            )
            
            messages.success(request, f'Entrada de stock registrada: +{cantidad} {producto.nombre}')
        else:
            messages.error(request, 'La cantidad debe ser mayor a cero.')
            
    return redirect('inventory:inventory_list')

@login_required
def stock_history(request):
    movimientos = StockMovement.objects.select_related('producto', 'user').all()
    context = {
        'movimientos': movimientos,
    }
    return render(request, 'inventory/stock_history.html', context)

@login_required
def product_history(request, pk):
    from django.shortcuts import get_object_or_404
    producto = get_object_or_404(Product, pk=pk)
    movimientos = producto.movimientos.select_related('user').all()
    context = {
        'producto': producto,
        'movimientos': movimientos,
    }
    return render(request, 'inventory/stock_history.html', context)

@login_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            categoria = form.save()
            messages.success(request, f'Categoría {categoria.nombre} creada con éxito.')
        else:
            messages.error(request, 'Error al crear la categoría. Verifique los datos.')
    return redirect('inventory:inventory_list')

@login_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            producto = form.save()
            messages.success(request, f'Producto {producto.nombre} creado con éxito.')
            return redirect('inventory:inventory_list')
    else:
        form = ProductForm()
        
    return render(request, 'inventory/product_form.html', {'form': form})

@login_required
def supplier_list(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            proveedor = form.save()
            messages.success(request, f'Proveedor {proveedor.nombre} registrado con éxito.')
            return redirect('inventory:supplier_list')
    else:
        form = SupplierForm()

    proveedores = Supplier.objects.all()
    
    # Estadísticas avanzadas de proveedores
    # 1. Total de items distintos suministrados (excluyendo servicios)
    total_items_suministrados = Product.objects.exclude(categoria__nombre='SERVICIOS').filter(proveedor__isnull=False).count()
    
    # 2. Valor total del inventario por proveedores
    total_valor_proveedores = Product.objects.exclude(categoria__nombre='SERVICIOS').filter(proveedor__isnull=False).aggregate(
        total=Sum(F('stock_actual') * F('precio'))
    )['total'] or 0
    
    context = {
        'proveedores': proveedores,
        'total_proveedores': proveedores.count(),
        'total_items': total_items_suministrados,
        'total_valor': total_valor_proveedores,
        'form': form,
    }
    return render(request, 'inventory/supplier_list.html', context)

@login_required
def product_update(request, pk):
    from django.shortcuts import get_object_or_404
    producto = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, f'Producto {producto.nombre} actualizado con éxito.')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error en {field}: {error}")
    return redirect('inventory:inventory_list')

@login_required
def supplier_detail(request, pk):
    from django.shortcuts import get_object_or_404
    proveedor = get_object_or_404(Supplier, pk=pk)
    productos = proveedor.productos.all()
    
    # Estadísticas específicas del proveedor
    total_items = productos.count()
    valor_total = productos.aggregate(
        total=Sum(F('stock_actual') * F('precio'))
    )['total'] or 0
    
    context = {
        'proveedor': proveedor,
        'productos': productos,
        'total_items': total_items,
        'valor_total': valor_total,
    }
    return render(request, 'inventory/supplier_detail.html', context)
