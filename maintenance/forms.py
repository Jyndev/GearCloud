from django import forms
from .models import MaintenanceOrder, MaintenanceSparePart
from users.models import User

class MultipleFileInput(forms.FileInput):
    allow_multiple_selected = True

    def value_from_datadict(self, data, files, name):
        if hasattr(files, 'getlist'):
            return files.getlist(name)
        return files.get(name)

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput(attrs={'class': 'form-control', 'multiple': True}))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class MaintenanceOrderForm(forms.ModelForm):
    fotos = MultipleFileField(
        required=False,
        label="Fotos del Vehículo"
    )

    class Meta:
        model = MaintenanceOrder
        fields = [
            'moto', 'kilometraje', 'gasolina', 
            'falla_reportada', 'observaciones_recepcion'
        ]
        widgets = {
            'moto': forms.Select(attrs={'class': 'form-select'}),
            'kilometraje': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 15000', 'autocomplete': 'off'}),
            'gasolina': forms.Select(attrs={'class': 'form-select'}),
            'falla_reportada': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describa el problema...', 'autocomplete': 'off'}),
            'observaciones_recepcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Estado físico de la moto...', 'autocomplete': 'off'}),
        }

class TechnicalUpdateForm(forms.ModelForm):
    class Meta:
        model = MaintenanceOrder
        fields = [
            'mecanico', 'diagnostico_tecnico', 
            'valor_diagnostico', 'costo_mano_obra'
        ]
        widgets = {
            'mecanico': forms.Select(attrs={'class': 'form-select', 'placeholder': ' '}),
            'diagnostico_tecnico': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'autocomplete': 'off', 'placeholder': ' '}),
            'valor_diagnostico': forms.NumberInput(attrs={'class': 'form-control', 'autocomplete': 'off', 'placeholder': ' '}),
            'costo_mano_obra': forms.NumberInput(attrs={'class': 'form-control', 'autocomplete': 'off', 'placeholder': ' '}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo mostrar usuarios con rol MECANICO
        queryset = User.objects.filter(role=User.ROLE_MECANICO)
        self.fields['mecanico'].queryset = queryset
        # Mostrar el nombre completo si existe, sino el username
        self.fields['mecanico'].label_from_instance = lambda obj: obj.get_full_name() or obj.username
