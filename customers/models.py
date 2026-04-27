from django.db import models

class Customer(models.Model):
    cedula = models.CharField(max_length=20, unique=True, verbose_name="Cédula o NIT")
    nombre = models.CharField(max_length=150, verbose_name="Nombre Completo o Razón Social")
    telefono = models.CharField(max_length=20, verbose_name="Número de Teléfono")
    direccion = models.CharField(max_length=255, blank=True, null=True, verbose_name="Dirección de Residencia")
    is_active = models.BooleanField(default=True, verbose_name="Cliente Activo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        # Convertir a mayúsculas para normalizar (NIT, CE, CC, etc)
        self.cedula = self.cedula.strip().upper()
        # Si la cédula contiene solo dígitos, asumimos que es Cédula de Ciudadanía y añadimos el prefijo
        if self.cedula.isdigit():
            self.cedula = f"CC {self.cedula}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} - CC/NIT: {self.cedula}"

    @property
    def whatsapp_url(self):
        # Limpiar el número de teléfono para que solo queden dígitos
        clean_phone = ''.join(filter(str.isdigit, self.telefono))
        # Si no empieza con el código de país (asumiendo Colombia 57 como default si tiene 10 dígitos)
        if len(clean_phone) == 10:
            clean_phone = '57' + clean_phone
        return f"https://wa.me/{clean_phone}"

class Motorcycle(models.Model):
    placa = models.CharField(max_length=10, primary_key=True, unique=True, verbose_name="Placa del Vehículo")
    owner = models.ForeignKey(Customer, on_delete=models.RESTRICT, related_name="motorcycles", verbose_name="Propietario del Vehículo")
    marca = models.CharField(max_length=50, verbose_name="Marca / Fabricante")
    modelo = models.CharField(max_length=100, verbose_name="Línea o Modelo")
    serial_motor = models.CharField(max_length=100, blank=True, null=True, verbose_name="Serial del Motor")
    serial_chasis = models.CharField(max_length=100, blank=True, null=True, verbose_name="Serial del Chasis")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Motocicleta"
        verbose_name_plural = "Motocicletas"
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.placa}] {self.marca} {self.modelo}"
