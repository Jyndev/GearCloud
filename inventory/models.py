from django.db import models

class Category(models.Model):
    nombre = models.CharField(max_length=150, unique=True, verbose_name="Nombre de Categoría")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.nombre

class Supplier(models.Model):
    nit = models.CharField(max_length=50, unique=True, verbose_name="NIT / Identificación")
    nombre = models.CharField(max_length=200, verbose_name="Razón Social / Nombre")
    contacto = models.CharField(max_length=150, blank=True, null=True, verbose_name="Persona de Contacto")
    telefono = models.CharField(max_length=50, blank=True, null=True, verbose_name="Teléfono")

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"

    def __str__(self):
        return f"{self.nombre} - {self.nit}"

class Product(models.Model):
    referencia = models.CharField(max_length=100, unique=True, verbose_name="Referencia / SKU")
    nombre = models.CharField(max_length=200, verbose_name="Nombre del Producto")
    categoria = models.ForeignKey(Category, on_delete=models.RESTRICT, related_name='productos', verbose_name="Categoría")
    proveedor = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name='productos', verbose_name="Proveedor")
    
    stock_actual = models.IntegerField(default=0, verbose_name="Stock Actual")
    stock_minimo = models.IntegerField(default=5, verbose_name="Stock Mínimo")
    precio_compra = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Precio de Compra")
    precio = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Precio de Venta")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    def __str__(self):
        return f"[{self.referencia}] {self.nombre}"

    @property
    def stock_bajo(self):
        return self.stock_actual <= self.stock_minimo

class StockMovement(models.Model):
    TIPO_MOVIMIENTO = [
        ('ENTRADA', 'Entrada (Compra/Suministro)'),
        ('SALIDA', 'Salida (Venta/Servicio)'),
        ('AJUSTE', 'Ajuste Manual'),
    ]

    producto = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='movimientos', verbose_name="Producto")
    tipo = models.CharField(max_length=15, choices=TIPO_MOVIMIENTO, verbose_name="Tipo de Movimiento")
    cantidad = models.IntegerField(verbose_name="Cantidad")
    precio_compra_instante = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Precio Compra en Movimiento")
    precio_venta_instante = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Precio Venta en Movimiento")
    user = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, verbose_name="Usuario Responsable")
    fecha = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y Hora")
    notas = models.TextField(blank=True, null=True, verbose_name="Notas/Observaciones")

    class Meta:
        verbose_name = "Movimiento de Stock"
        verbose_name_plural = "Movimientos de Stock"
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.tipo} - {self.producto.nombre} ({self.cantidad})"
