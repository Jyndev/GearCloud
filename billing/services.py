from django.db import transaction
from .models import Invoice, InvoiceItem
from inventory.services import registrar_salida_inventario

@transaction.atomic
def crear_factura(items_data, cliente=None, cliente_nombre=None, user=None):
    """
    Crea una factura y sus lineas de detalle, descontando el stock correspondiente.
    items_data es una lista de diccionarios con {'producto_id': int, 'cantidad': int, 'precio_unitario': decimal}
    """
    # Generar un consecutivo sencillo
    last_invoice = Invoice.objects.order_by('id').last()
    consecutivo_num = last_invoice.id + 1 if last_invoice else 1
    consecutivo = f"FAC-{consecutivo_num:04d}"

    factura = Invoice.objects.create(
        consecutivo=consecutivo,
        cliente=cliente,
        cliente_nombre=cliente_nombre,
        estado='PAGADA' # Por defecto asumimos que se paga al instante en mostrador
    )

    subtotal_factura = 0

    for item in items_data:
        producto_id = item['producto_id']
        cantidad = item['cantidad']
        precio_unitario = item['precio_unitario']
        subtotal_item = cantidad * precio_unitario

        # Descuento de stock (esta llamada es atómica y registra el movimiento)
        registrar_salida_inventario(producto_id, cantidad, user=user)

        InvoiceItem.objects.create(
            factura=factura,
            producto_id=producto_id,
            cantidad=cantidad,
            precio_unitario=precio_unitario,
            subtotal=subtotal_item
        )
        
        subtotal_factura += subtotal_item

    factura.subtotal = subtotal_factura
    factura.total = subtotal_factura # Asumiendo no hay impuestos extras por ahora según modelo
    factura.save(update_fields=['subtotal', 'total'])

    return factura
