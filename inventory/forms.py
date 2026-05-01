from django import forms
from .models import Product, Supplier, Category

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['referencia', 'nombre', 'categoria', 'proveedor', 'stock_actual', 'stock_minimo', 'precio', 'is_active']
        widgets = {
            'referencia': forms.TextInput(attrs={'autocomplete': 'off', 'class': 'form-control', 'placeholder': ' '}),
            'nombre': forms.TextInput(attrs={'autocomplete': 'off', 'class': 'form-control', 'placeholder': ' '}),
            'categoria': forms.Select(attrs={'autocomplete': 'off', 'class': 'form-select'}),
            'proveedor': forms.Select(attrs={'autocomplete': 'off', 'class': 'form-select'}),
            'stock_actual': forms.NumberInput(attrs={'autocomplete': 'off', 'class': 'form-control', 'placeholder': ' '}),
            'stock_minimo': forms.NumberInput(attrs={'autocomplete': 'off', 'class': 'form-control', 'placeholder': ' '}),
            'precio': forms.NumberInput(attrs={'autocomplete': 'off', 'class': 'form-control', 'placeholder': ' '}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['stock_actual'].required = False

    def clean_precio(self):
        precio = self.cleaned_data.get('precio')
        if precio is not None and precio < 0:
            raise forms.ValidationError('El precio no puede ser negativo.')
        return precio

    def clean_stock_actual(self):
        stock = self.cleaned_data.get('stock_actual')
        if stock is not None and stock < 0:
            raise forms.ValidationError('El stock actual no puede ser negativo.')
        return stock
        
    def clean_stock_minimo(self):
        stock = self.cleaned_data.get('stock_minimo')
        if stock is not None and stock < 0:
            raise forms.ValidationError('El stock mínimo no puede ser negativo.')
        return stock

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['nit', 'nombre', 'contacto', 'telefono']
        widgets = {
            'nit': forms.TextInput(attrs={'autocomplete': 'off', 'class': 'form-control', 'placeholder': ' '}),
            'nombre': forms.TextInput(attrs={'autocomplete': 'off', 'class': 'form-control', 'placeholder': ' '}),
            'contacto': forms.TextInput(attrs={'autocomplete': 'off', 'class': 'form-control', 'placeholder': ' '}),
            'telefono': forms.TextInput(attrs={'autocomplete': 'off', 'class': 'form-control', 'placeholder': ' '}),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'autocomplete': 'off', 'class': 'form-control', 'placeholder': ' '}),
            'descripcion': forms.Textarea(attrs={'autocomplete': 'off', 'class': 'form-control', 'placeholder': ' ', 'rows': 3}),
        }
