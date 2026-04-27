from django import forms
from .models import Customer, Motorcycle

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['cedula', 'nombre', 'telefono', 'direccion', 'is_active']
        labels = {
            'cedula': 'Cédula o NIT',
            'nombre': 'Nombre o Razón Social',
            'telefono': 'Número de Teléfono',
            'direccion': 'Dirección de Residencia',
            'is_active': 'Cliente Activo',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            else:
                field.widget.attrs.update({
                    'class': 'form-control', 
                    'autocomplete': 'off',
                    'placeholder': ' ' # Para floating labels
                })


class MotorcycleForm(forms.ModelForm):
    class Meta:
        model = Motorcycle
        fields = ['placa', 'marca', 'modelo', 'serial_motor', 'serial_chasis']
        labels = {
            'placa': 'Placa del Vehículo',
            'marca': 'Marca / Fabricante',
            'modelo': 'Línea o Modelo',
            'serial_motor': 'Serial del Motor (Opcional)',
            'serial_chasis': 'Serial del Chasis (Opcional)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control', 
                'autocomplete': 'off',
                'placeholder': ' ' # Para floating labels
            })
