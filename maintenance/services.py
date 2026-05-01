from django.db import transaction
from django.core.exceptions import ValidationError
from inventory.models import Product, StockMovement
from .models import MaintenanceOrder, MaintenanceSparePart

class MaintenanceService:
    @staticmethod
    @transaction.atomic
    def add_spare_part(order_id, product_id, cantidad, user=None):
        """
        Añade un repuesto a la orden y descuenta el stock instantáneamente.
        """
        try:
            order = MaintenanceOrder.objects.get(id=order_id)
            product = Product.objects.get(id=product_id)
        except (MaintenanceOrder.DoesNotExist, Product.DoesNotExist) as e:
            raise ValidationError(f"Recurso no encontrado: {str(e)}")

        if product.stock_actual < cantidad:
            raise ValidationError(f"Stock insuficiente para {product.nombre}. Disponible: {product.stock_actual}")

        # Crear el registro del repuesto en la orden
        spare_part = MaintenanceSparePart.objects.create(
            order=order,
            product=product,
            cantidad=cantidad,
            precio_unitario=product.precio  # Captura el precio actual de venta
        )

        # Descontar stock
        product.stock_actual -= cantidad
        product.save()

        # Registrar movimiento de stock
        StockMovement.objects.create(
            producto=product,
            tipo='SALIDA',
            cantidad=cantidad,
            precio_compra_instante=product.precio_compra,
            precio_venta_instante=product.precio,
            user=user,
            notas=f"Salida por Servicio - Orden {order.codigo_ot}"
        )

        return spare_part

    @staticmethod
    def transition_state(order_id, new_state, user=None):
        """
        Cambia el estado de la orden validando condiciones de negocio.
        """
        order = MaintenanceOrder.objects.get(id=order_id)
        
        # Validaciones de negocio por estado
        if new_state == 'REVISION' and not order.mecanico:
            raise ValidationError("Debe asignar un mecánico antes de pasar a Revisión.")
        
        if new_state == 'COMPLETADO':
            if not order.diagnostico_tecnico:
                raise ValidationError("No se puede completar sin un diagnóstico técnico.")
            if order.total_general <= 0:
                # Opcional: advertencia si no hay cargos, pero el usuario dijo que puede ser solo diagnóstico.
                pass

        order.estado = new_state
        order.save()
        return order
