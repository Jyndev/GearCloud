from django.urls import path
from . import views

app_name = 'maintenance'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('<int:pk>/estado/', views.UpdateStatusView.as_view(), name='update_status'),
    path('search-products/', views.search_products, name='search_products'),
    path('<int:pk>/add-part/', views.add_spare_part, name='add_spare_part'),
    path('spare-part/<int:pk>/delete/', views.delete_spare_part, name='delete_spare_part'),
    path('<int:pk>/complete/', views.complete_order, name='complete_order'),
]
