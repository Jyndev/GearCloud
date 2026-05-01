from django.contrib import admin
from .models import MaintenanceOrder, MaintenanceSparePart

class SparePartInline(admin.TabularInline):
    model = MaintenanceSparePart
    extra = 1

@admin.register(MaintenanceOrder)
class MaintenanceOrderAdmin(admin.ModelAdmin):
    list_display = ('codigo_ot', 'moto', 'estado', 'mecanico', 'total_general', 'created_at')
    list_filter = ('estado', 'created_at')
    search_fields = ('codigo_ot', 'moto__placa')
    inlines = [SparePartInline]
    readonly_fields = ('codigo_ot',)
