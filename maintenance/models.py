from django.db import models
from django.conf import settings
from customers.models import Motorcycle
from inventory.models import Product

class MaintenanceOrder(models.Model):
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('REVISION', 'En Revisión'),
        ('REPARACION', 'En Reparación'),
        ('COMPLETADO', 'Completado'),
        ('ENTREGADO', 'Entregado'),
    ]

    NIVELES_GASOLINA = [
        ('1/4', '1/4'),
        ('1/2', '1/2'),
        ('3/4', '3/4'),
        ('LLENO', 'Lleno'),
        ('RESERVA', 'Reserva'),
    ]

    codigo_ot = models.CharField(max_length=20, unique=True, editable=False, verbose_name="Código OT")
    moto = models.ForeignKey(Motorcycle, on_delete=models.CASCADE, related_name='ordenes', verbose_name="Motocicleta")
    recepcionista = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='ordenes_recibidas', verbose_name="Recibido por")
    mecanico = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='ordenes_asignadas', verbose_name="Mecánico Asignado")
    
    kilometraje = models.IntegerField(verbose_name="Kilometraje Actual")
    gasolina = models.CharField(max_length=10, choices=NIVELES_GASOLINA, verbose_name="Nivel de Gasolina")
    falla_reportada = models.TextField(verbose_name="Falla Reportada / Motivo")
    observaciones_recepcion = models.TextField(blank=True, null=True, verbose_name="Observaciones de Recepción")
    
    diagnostico_tecnico = models.TextField(blank=True, null=True, verbose_name="Diagnóstico Técnico")
    valor_diagnostico = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Valor Diagnóstico")
    costo_mano_obra = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Costo Mano de Obra")
    
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE', verbose_name="Estado de la Orden")
    factura = models.OneToOneField('billing.Invoice', on_delete=models.SET_NULL, null=True, blank=True, related_name='orden_mantenimiento', verbose_name="Factura Asociada")
    
    comision_pagada = models.BooleanField(default=False, verbose_name="Comisión Pagada")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")

    class Meta:
        verbose_name = "Orden de Mantenimiento"
        verbose_name_plural = "Órdenes de Mantenimiento"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.codigo_ot:
            last_order = MaintenanceOrder.objects.all().order_by('id').last()
            if not last_order:
                self.codigo_ot = 'OT-0001'
            else:
                try:
                    # Intenta extraer el número del último código
                    last_num = int(last_order.codigo_ot.split('-')[1])
                    self.codigo_ot = f'OT-{str(last_num + 1).zfill(4)}'
                except (IndexError, ValueError):
                    # Si falla, simplemente usa el ID
                    count = MaintenanceOrder.objects.count()
                    self.codigo_ot = f'OT-{str(count + 1).zfill(4)}'
        
        # Al asignar un mecánico, cambiar estado a REVISION si estaba en PENDIENTE
        if self.mecanico and self.estado == 'PENDIENTE':
            self.estado = 'REVISION'
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.codigo_ot} - {self.moto.placa}"

    @property
    def total_repuestos(self):
        return sum(item.subtotal for item in self.repuestos.all())

    @property
    def total_general(self):
        return self.total_repuestos + self.valor_diagnostico + self.costo_mano_obra

class MaintenanceSparePart(models.Model):
    order = models.ForeignKey(MaintenanceOrder, on_delete=models.CASCADE, related_name='repuestos', verbose_name="Orden")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="Repuesto/Producto")
    cantidad = models.IntegerField(default=1, verbose_name="Cantidad")
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Precio Unitario")

    class Meta:
        verbose_name = "Repuesto de Mantenimiento"
        verbose_name_plural = "Repuestos de Mantenimiento"

    def __str__(self):
        return f"{self.product.nombre} x {self.cantidad}"

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario

class MaintenancePhoto(models.Model):
    order = models.ForeignKey(MaintenanceOrder, on_delete=models.CASCADE, related_name='fotos', verbose_name="Orden")
    imagen = models.FileField(upload_to='maintenance/photos/%Y/%m/%d/', verbose_name="Fotografía")
    descripcion = models.CharField(max_length=200, blank=True, null=True, verbose_name="Descripción de la foto")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Fotografía de Mantenimiento"
        verbose_name_plural = "Fotografías de Mantenimiento"
