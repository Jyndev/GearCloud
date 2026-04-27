from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from .forms import CustomLoginForm

class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    authentication_form = CustomLoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        # Manejo de sesion (Recordarme)
        remember_me = form.cleaned_data.get('remember_me')
        if not remember_me:
            # Si no activa recordarme, la sesión expira cuando se cierra el navegador
            self.request.session.set_expiry(0)
            self.request.session.modified = True
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('dashboard:index')

from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from .models import User
from .forms import UserManagementForm, UserEditForm

def is_admin(user):
    return user.is_authenticated and user.is_admin()

admin_required = user_passes_test(is_admin, login_url='users:login')

@method_decorator(admin_required, name='dispatch')
class UserListView(ListView):
    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'users'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_form'] = UserManagementForm()
        # No mandamos form de edición base porque dependerá del usuario. Usaremos fetch o recargar en un caso simple,
        # pero al ser vista de modales podemos instanciar formularios para POST sencillos
        return context

@admin_required
def create_user(request):
    if request.method == 'POST':
        form = UserManagementForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario creado exitosamente.")
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.accepts('application/json'):
                return JsonResponse({'success': True})
            return redirect('users:user_list')
        else:
            field_labels = {
                'username': 'Nombre de usuario',
                'email': 'Correo electrónico',
                'password1': 'Contraseña',
                'password2': 'Confirmación de contraseña',
                'first_name': 'Nombres',
                'last_name': 'Apellidos',
                'role': 'Rol'
            }
            error_msg = "Error en los datos:<br>"
            for field, errors in form.errors.items():
                label = field_labels.get(field, field)
                error_msg += f"<b>{label}</b>: {', '.join(errors)}<br>"
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.accepts('application/json'):
                return JsonResponse({'success': False, 'error_html': error_msg})
                
            messages.error(request, error_msg)
    return redirect('users:user_list')

@admin_required
def update_user(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario actualizado exitosamente.")
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.accepts('application/json'):
                return JsonResponse({'success': True})
            return redirect('users:user_list')
        else:
            error_msg = "Error en los datos:<br>"
            for field, errors in form.errors.items():
                error_msg += f"<b>{field}</b>: {', '.join(errors)}<br>"
                
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.accepts('application/json'):
                return JsonResponse({'success': False, 'error_html': error_msg})
                
            messages.error(request, error_msg)
    return redirect('users:user_list')

@admin_required
def toggle_user_status(request, pk):
    if request.method == 'POST':
        user_obj = get_object_or_404(User, pk=pk)
        # Prevención: No desactivarse a sí mismo
        if user_obj == request.user:
            messages.error(request, "No puedes desactivar tu propia cuenta.")
            return redirect('users:user_list')
            
        user_obj.is_active = not user_obj.is_active
        user_obj.save()
        estado = "activado" if user_obj.is_active else "desactivado"
        messages.success(request, f"Usuario {estado} lógicamente con éxito.")
    return redirect('users:user_list')

