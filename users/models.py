from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_ADMIN = 'ADMIN'
    ROLE_MECANICO = 'MECANICO'
    ROLE_RECEPCION = 'RECEPCION'

    ROLES = [
        (ROLE_ADMIN, 'Administrador'),
        (ROLE_MECANICO, 'Mecánico'),
        (ROLE_RECEPCION, 'Recepción'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLES,
        default=ROLE_RECEPCION,
        verbose_name="Rol en el sistema"
    )
    
    comision_porcentaje = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=50.00,
        verbose_name="Porcentaje de Comisión (%)",
        help_text="Porcentaje de la mano de obra que recibe el mecánico"
    )

    def is_admin(self):
        return self.role == self.ROLE_ADMIN

    def is_mecanico(self):
        return self.role == self.ROLE_MECANICO

    def is_recepcion(self):
        return self.role == self.ROLE_RECEPCION

    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"
