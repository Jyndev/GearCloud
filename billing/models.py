from django.db import models
from customers.models import Customer
from inventory.models import Product

class Invoice(models.Model):
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('PAGADA', 'Pagada'),
        ('ANULADA', 'Anulada'),
    ]

    consecutivo = models.CharField(max_length=20, unique=True, verbose_name="Número de Factura")
    cliente = models.ForeignKey(Customer, on_delete=models.RESTRICT, related_name='facturas', verbose_name="Cliente", null=True, blank=True)
    cliente_nombre = models.CharField(max_length=200, blank=True, null=True, verbose_name="Nombre Cliente (Manual)")
    fecha = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Emisión")
    estado = models.CharField(max_length=15, choices=ESTADOS, default='PENDIENTE', verbose_name="Estado")
    
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Subtotal")
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Total")

    class Meta:
        verbose_name = "Factura"
        verbose_name_plural = "Facturas"
        ordering = ['-fecha']

    def __str__(self):
        cliente_label = self.cliente.nombre if self.cliente else (self.cliente_nombre or "Consumidor Final")
        return f"{self.consecutivo} - {cliente_label}"

class InvoiceItem(models.Model):
    factura = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items', verbose_name="Factura")
    producto = models.ForeignKey(Product, on_delete=models.RESTRICT, related_name='facturados', verbose_name="Producto")
    cantidad = models.IntegerField(verbose_name="Cantidad")
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Precio Unitario")
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Subtotal")

    class Meta:
        verbose_name = "Detalle de Factura"
        verbose_name_plural = "Detalles de Facturas"

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"
