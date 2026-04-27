from django import forms
from django.contrib.auth.forms import AuthenticationForm

class CustomLoginForm(AuthenticationForm):
    remember_me = forms.BooleanField(required=False)
    
    # We redefine username and password just to avoid Django's default styling
    # and instead control everything from the template safely.
    username = forms.CharField(
        label="Nombre de usuario",
        widget=forms.TextInput(attrs={
            'id': 'username',
            'placeholder': ' ',
            'required': True,
            'autocomplete': 'off',
        })
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            'id': 'password',
            'placeholder': ' ',
            'required': True,
            'autocomplete': 'off',
        })
    )

from django.contrib.auth.forms import UserCreationForm
from .models import User

class UserManagementForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role')
        labels = {
            'username': 'Nombre de usuario',
            'email': 'Correo electrónico',
            'first_name': 'Nombres',
            'last_name': 'Apellidos',
            'role': 'Rol del sistema',
            'password1': 'Contraseña',
            'password2': 'Confirmar contraseña',
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control', 
                'autocomplete': 'off',
                'placeholder': ' ' # Requerido para CSS floating labels
            })
        self.fields['role'].widget.attrs.update({'required': 'required'})

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active')
        labels = {
            'username': 'Nombre de usuario',
            'email': 'Correo electrónico',
            'first_name': 'Nombres',
            'last_name': 'Apellidos',
            'role': 'Rol del sistema',
            'is_active': 'Usuario activo',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'autocomplete': 'off', 'required': 'required'})
            else:
                field.widget.attrs.update({
                    'class': 'form-control', 
                    'autocomplete': 'off',
                    'placeholder': ' ' # Requerido para CSS floating labels
                })
