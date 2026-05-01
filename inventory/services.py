from django.db import transaction
from django.core.exceptions import ValidationError
from django.db.models import F
from .models import Product, StockMovement

@transaction.atomic
def registrar_salida_inventario(producto_id, cantidad, user=None):
    """
    Descuenta la cantidad del stock del producto de forma atómica y registra el movimiento.
    Lanza ValidationError si no hay suficiente stock.
    """
    producto = Product.objects.select_for_update().get(pk=producto_id)
    if producto.stock_actual < cantidad:
        raise ValidationError(f"Stock insuficiente para {producto.nombre}. Stock actual: {producto.stock_actual}")
    
    # 1. Registrar el movimiento en el historial antes de descontar (o después, dentro del atomic)
    StockMovement.objects.create(
        producto=producto,
        tipo='SALIDA',
        cantidad=cantidad,
        precio_compra_instante=producto.precio_compra,
        precio_venta_instante=producto.precio,
        user=user,
        notas="Salida registrada por venta/facturación."
    )

    # 2. Descontar el stock
    producto.stock_actual = F('stock_actual') - cantidad
    producto.save(update_fields=['stock_actual'])
    producto.refresh_from_db()
    
    return producto

def ensure_default_services():
    """
    Garantiza que existan los productos básicos de servicios (Mano de Obra y Diagnóstico)
    y su categoría correspondiente.
    """
    from .models import Category, Product
    # 1. Asegurar categoría
    cat_servicios, _ = Category.objects.get_or_create(
        nombre="SERVICIOS",
        defaults={'descripcion': 'Servicios técnicos y mano de obra del taller'}
    )
    
    # 2. Asegurar Mano de Obra
    Product.objects.get_or_create(
        referencia="SER-MO",
        defaults={
            'nombre': "MANO DE OBRA / SERVICIO",
            'categoria': cat_servicios,
            'precio': 0,
            'stock_actual': 0,
            'is_active': True
        }
    )
    
    # 3. Asegurar Diagnóstico
    Product.objects.get_or_create(
        referencia="SER-DIAG",
        defaults={
            'nombre': "DIAGNÓSTICO TÉCNICO",
            'categoria': cat_servicios,
            'precio': 0,
            'stock_actual': 0,
            'is_active': True
        }
    )
