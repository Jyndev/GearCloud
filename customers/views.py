from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Sum, Q
from .models import Customer, Motorcycle
from .forms import CustomerForm, MotorcycleForm
from maintenance.models import MaintenanceOrder
from billing.models import Invoice

def is_reception_or_admin(user):
    return user.is_authenticated and user.role in ['ADMIN', 'RECEPCION']

reception_required = user_passes_test(is_reception_or_admin, login_url='users:login')

@method_decorator(reception_required, name='dispatch')
class CustomerListView(ListView):
    model = Customer
    template_name = 'customers/customer_list.html'
    context_object_name = 'customers'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_form'] = CustomerForm()
        return context

@reception_required
def create_customer(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Cliente registrado exitosamente.")
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.accepts('application/json'):
                return JsonResponse({'success': True})
            return redirect('customers:customer_list')
        else:
            field_labels = {
                'cedula': 'Cédula o NIT',
                'nombre': 'Nombre o Razón Social',
                'telefono': 'Número de Teléfono',
                'direccion': 'Dirección',
            }
            error_msg = "Error en los datos:<br>"
            for field, errors in form.errors.items():
                label = field_labels.get(field, field)
                error_msg += f"<b>{label}</b>: {', '.join(errors)}<br>"
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.accepts('application/json'):
                return JsonResponse({'success': False, 'error_html': error_msg})
                
            messages.error(request, error_msg)
    return redirect('customers:customer_list')

@reception_required
def update_customer(request, pk):
    customer_obj = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Datos del cliente actualizados.")
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.accepts('application/json'):
                return JsonResponse({'success': True})
            return redirect('customers:customer_list')
        else:
            error_msg = "Error en los datos:<br>"
            for field, errors in form.errors.items():
                error_msg += f"<b>{field}</b>: {', '.join(errors)}<br>"
                
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.accepts('application/json'):
                return JsonResponse({'success': False, 'error_html': error_msg})
                
            messages.error(request, error_msg)
    return redirect('customers:customer_list')

@reception_required
def customer_detail(request, pk):
    customer_obj = get_object_or_404(Customer, pk=pk)
    motos = customer_obj.motorcycles.all()
    create_form = MotorcycleForm()
    
    # --- Estadísticas del Cliente ---
    # Total de órdenes vinculadas a sus motos
    total_orders = MaintenanceOrder.objects.filter(moto__owner=customer_obj).count()
    
    # Mantenimientos completados o entregados
    completed_orders = MaintenanceOrder.objects.filter(
        moto__owner=customer_obj,
        estado__in=['COMPLETADO', 'ENTREGADO']
    ).count()
    
    # Total invertido por el cliente (suma de facturas pagadas)
    total_spent = Invoice.objects.filter(
        cliente=customer_obj,
        estado='PAGADA'
    ).aggregate(total=Sum('total'))['total'] or 0
    
    # Historial de Servicios (Ordenes de mantenimiento)
    service_history = MaintenanceOrder.objects.filter(
        moto__owner=customer_obj
    ).select_related('moto').order_by('-created_at')
    
    return render(request, 'customers/customer_detail.html', {
        'customer': customer_obj,
        'motos': motos,
        'create_form': create_form,
        'stats': {
            'total_orders': total_orders,
            'completed_orders': completed_orders,
            'total_spent': total_spent,
        },
        'service_history': service_history
    })


@reception_required
def add_motorcycle(request, customer_pk):
    customer_obj = get_object_or_404(Customer, pk=customer_pk)
    
    if not customer_obj.is_active:
        msg = "No se pueden registrar vehículos para un cliente inactivo. Por favor, actívalo primero."
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.accepts('application/json'):
            return JsonResponse({'success': False, 'error_html': msg})
        messages.error(request, msg)
        return redirect('customers:customer_detail', pk=customer_pk)

    if request.method == 'POST':
        # Instanciamos el form con los datos, pero no salvamos aun
        form = MotorcycleForm(request.POST)
        if form.is_valid():
            moto = form.save(commit=False)
            moto.owner = customer_obj
            moto.save()
            messages.success(request, "Motocicleta añadida exitosamente.")
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.accepts('application/json'):
                return JsonResponse({'success': True})
        else:
            error_msg = "Error en los datos de la moto:<br>"
            for field, errors in form.errors.items():
                error_msg += f"<b>{field}</b>: {', '.join(errors)}<br>"
                
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.accepts('application/json'):
                return JsonResponse({'success': False, 'error_html': error_msg})
            messages.error(request, error_msg)
            
    return redirect('customers:customer_detail', pk=customer_pk)
@reception_required
def toggle_customer_status(request, pk):
    customer_obj = get_object_or_404(Customer, pk=pk)
    customer_obj.is_active = not customer_obj.is_active
    customer_obj.save()
    status = "activado" if customer_obj.is_active else "desactivado"
    messages.info(request, f"Cliente {customer_obj.nombre} ha sido {status}.")
    return redirect('customers:customer_detail', pk=pk)
