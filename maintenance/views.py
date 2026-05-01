from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, DetailView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.http import JsonResponse
from .models import MaintenanceOrder, MaintenanceSparePart
from .forms import MaintenanceOrderForm, TechnicalUpdateForm
from .services import MaintenanceService

class DashboardView(LoginRequiredMixin, ListView):
    model = MaintenanceOrder
    template_name = 'maintenance/dashboard.html'
    context_object_name = 'ordenes'

    def get_context_data(self, **kwargs):
        from .forms import MaintenanceOrderForm
        context = super().get_context_data(**kwargs)
        # Separar órdenes por estado para el Kanban
        context['pendientes'] = MaintenanceOrder.objects.filter(estado='PENDIENTE').select_related('moto', 'mecanico')
        context['revision'] = MaintenanceOrder.objects.filter(estado='REVISION').select_related('moto', 'mecanico')
        context['reparacion'] = MaintenanceOrder.objects.filter(estado='REPARACION').select_related('moto', 'mecanico')
        context['completadas'] = MaintenanceOrder.objects.filter(estado='COMPLETADO').select_related('moto', 'mecanico')
        
        if 'form_creacion' not in context:
            context['form_creacion'] = MaintenanceOrderForm()
        return context

    def post(self, request, *args, **kwargs):
        if request.user.role not in ['ADMIN', 'RECEPCION']:
            messages.error(request, "No tienes permiso para crear órdenes de servicio.")
            return redirect('maintenance:dashboard')
            
        from .forms import MaintenanceOrderForm
        from .models import MaintenancePhoto
        form = MaintenanceOrderForm(request.POST, request.FILES)
        if form.is_valid():
            order = form.save(commit=False)
            order.recepcionista = request.user
            order.save()
            
            # Guardar múltiples fotos
            fotos = request.FILES.getlist('fotos')
            for f in fotos:
                MaintenancePhoto.objects.create(order=order, imagen=f)
                
            messages.success(request, f"¡Éxito! Orden {order.codigo_ot} creada correctamente.")
            return redirect('maintenance:dashboard')
        
        # Si el formulario falla, recargar el dashboard con errores
        self.object_list = self.get_queryset()
        return self.render_to_response(self.get_context_data(form_creacion=form))


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = MaintenanceOrder
    template_name = 'maintenance/order_detail.html'
    context_object_name = 'orden'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'form_tecnico' not in context:
            context['form_tecnico'] = TechnicalUpdateForm(instance=self.object)
            
        # Si la orden ya está completada, deshabilitar edición en el formulario
        if self.object.estado in ['COMPLETADO', 'ENTREGADO']:
            for field in context['form_tecnico'].fields.values():
                field.disabled = True
                
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        # Bloquear guardado si ya está completada
        if self.object.estado in ['COMPLETADO', 'ENTREGADO']:
            messages.error(request, "No se puede modificar una orden que ya ha sido finalizada.")
            return redirect('maintenance:order_detail', pk=self.object.pk)

        form = TechnicalUpdateForm(request.POST, instance=self.object)
        if form.is_valid():
            form.save()
            messages.success(request, "Datos técnicos actualizados.")
            return redirect('maintenance:order_detail', pk=self.object.pk)
        return self.render_to_response(self.get_context_data(form_tecnico=form))

class UpdateStatusView(LoginRequiredMixin, View):
    def post(self, request, pk):
        new_state = request.POST.get('nuevo_estado')
        
        try:
            MaintenanceService.transition_state(pk, new_state, request.user)
            messages.success(request, f"Estado actualizado a {new_state}.")
        except Exception as e:
            messages.error(request, str(e))
        return redirect('maintenance:order_detail', pk=pk)

def search_products(request):
    q = request.GET.get('q', '')
    if q:
        from inventory.models import Product
        from django.db.models import Q
        products = Product.objects.filter(
            Q(nombre__icontains=q) | 
            Q(referencia__icontains=q)
        ).filter(is_active=True).exclude(categoria__nombre="SERVICIOS").distinct()[:10]
        
        results = []
        for p in products:
            results.append({
                'id': p.id,
                'nombre': p.nombre,
                'referencia': p.referencia,
                'stock': p.stock_actual,
                'precio': float(p.precio)
            })
        return JsonResponse({'results': results})
    return JsonResponse({'results': []})

def add_spare_part(request, pk):
    from inventory.models import Product, StockMovement
    if request.method == 'POST':
        orden = get_object_or_404(MaintenanceOrder, pk=pk)
        
        # Validar que la orden no esté cerrada
        if orden.estado in ['COMPLETADO', 'ENTREGADO']:
            messages.error(request, "No se pueden añadir repuestos a una orden finalizada.")
            return redirect('maintenance:order_detail', pk=pk)

        product_id = request.POST.get('product_id')
        cantidad = int(request.POST.get('cantidad', 1))
        
        product = get_object_or_404(Product, id=product_id)
        
        if product.stock_actual < cantidad:
            messages.error(request, f"Stock insuficiente para {product.nombre}. Disponible: {product.stock_actual}")
        else:
            from .models import MaintenanceSparePart
            spare, created = MaintenanceSparePart.objects.get_or_create(
                order=orden,
                product=product,
                defaults={'precio_unitario': product.precio, 'cantidad': 0}
            )
            spare.cantidad += cantidad
            spare.save()
            
            StockMovement.objects.create(
                producto=product,
                tipo='SALIDA',
                cantidad=cantidad,
                precio_compra_instante=product.precio_compra,
                precio_venta_instante=product.precio,
                user=request.user,
                notas=f"Consumo en OT {orden.codigo_ot}"
            )
            
            product.stock_actual -= cantidad
            product.save()
            
            messages.success(request, f"Se agregó {cantidad}x {product.nombre} a la orden.")
            
    return redirect(reverse('maintenance:order_detail', kwargs={'pk': pk}) + '#tab-parts')

def delete_spare_part(request, pk):
    from .models import MaintenanceSparePart
    from inventory.models import StockMovement
    spare_part = get_object_or_404(MaintenanceSparePart, pk=pk)
    order_id = spare_part.order.id
    
    # Validar que la orden no esté cerrada
    if spare_part.order.estado in ['COMPLETADO', 'ENTREGADO']:
        messages.error(request, "No se pueden eliminar repuestos de una orden finalizada.")
        return redirect('maintenance:order_detail', pk=order_id)

    product = spare_part.product
    cantidad = spare_part.cantidad

    if request.method == 'POST':
        # 1. Devolver stock al producto
        product.stock_actual += cantidad
        product.save()

        # 2. Registrar movimiento de stock de entrada
        StockMovement.objects.create(
            producto=product,
            tipo='ENTRADA',
            cantidad=cantidad,
            precio_compra_instante=product.precio_compra,
            precio_venta_instante=product.precio,
            user=request.user,
            notas=f"Devolución por eliminación - OT {spare_part.order.codigo_ot}"
        )

        # 3. Eliminar el registro del repuesto
        spare_part.delete()
        messages.warning(request, f"Se eliminó {product.nombre} de la orden y se restauró el stock.")

    return redirect(reverse('maintenance:order_detail', kwargs={'pk': order_id}) + '#tab-parts')

def complete_order(request, pk):
    from billing.models import Invoice, InvoiceItem
    from inventory.models import Product, Category
    
    orden = get_object_or_404(MaintenanceOrder, pk=pk)
    
    if request.method == 'POST':
        if orden.estado != 'COMPLETADO' and not orden.factura:
            # 1. Generar Factura
            last_invoice = Invoice.objects.order_by('id').last()
            if not last_invoice:
                consecutivo = "FAC-0001"
            else:
                try:
                    last_num = int(last_invoice.consecutivo.split('-')[1])
                    consecutivo = f"FAC-{str(last_num + 1).zfill(4)}"
                except (IndexError, ValueError):
                    consecutivo = f"FAC-{Invoice.objects.count() + 1:04d}"
                
            invoice = Invoice.objects.create(
                consecutivo=consecutivo,
                cliente=orden.moto.owner,
                subtotal=orden.total_general,
                total=orden.total_general,
                estado='PENDIENTE'
            )
            
            # 2. Items de repuestos
            for spare in orden.repuestos.all():
                InvoiceItem.objects.create(
                    factura=invoice,
                    producto=spare.product,
                    cantidad=spare.cantidad,
                    precio_unitario=spare.precio_unitario,
                    subtotal=spare.subtotal
                )
                
            # 3. Rubros de servicios (Mano de obra y diagnóstico)
            cat_servicios, _ = Category.objects.get_or_create(nombre="SERVICIOS")
            
            if orden.costo_mano_obra > 0:
                prod_mo, _ = Product.objects.get_or_create(
                    referencia="SER-MO",
                    defaults={'nombre': "MANO DE OBRA / SERVICIO", 'categoria': cat_servicios, 'precio': 0}
                )
                InvoiceItem.objects.create(
                    factura=invoice, producto=prod_mo, cantidad=1,
                    precio_unitario=orden.costo_mano_obra, subtotal=orden.costo_mano_obra
                )
                
            if orden.valor_diagnostico > 0:
                prod_diag, _ = Product.objects.get_or_create(
                    referencia="SER-DIAG",
                    defaults={'nombre': "DIAGNÓSTICO TÉCNICO", 'categoria': cat_servicios, 'precio': 0}
                )
                InvoiceItem.objects.create(
                    factura=invoice, producto=prod_diag, cantidad=1,
                    precio_unitario=orden.valor_diagnostico, subtotal=orden.valor_diagnostico
                )
            
            # 4. Vincular y cambiar estado
            orden.factura = invoice
            orden.estado = 'COMPLETADO'
            orden.save()
            
            messages.success(request, f"Mantenimiento finalizado. Factura {invoice.consecutivo} generada.")
        else:
            messages.info(request, "Esta orden ya ha sido finalizada o tiene una factura asociada.")
            
    return redirect('maintenance:order_detail', pk=pk)
