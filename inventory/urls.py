from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.inventory_list, name='inventory_list'),
    path('history/', views.stock_history, name='stock_history'),
    path('product/new/', views.product_create, name='product_create'),
    path('product/<int:pk>/stock-entry/', views.stock_entry, name='stock_entry'),
    path('product/<int:pk>/edit/', views.product_update, name='product_update'),
    path('product/<int:pk>/history/', views.product_history, name='product_history'),
    path('category/new/', views.category_create, name='category_create'),
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('supplier/<int:pk>/', views.supplier_detail, name='supplier_detail'),
]
