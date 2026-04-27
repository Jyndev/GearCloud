from django.urls import path
from . import views

app_name = 'customers'

urlpatterns = [
    path('management/', views.CustomerListView.as_view(), name='customer_list'),
    path('create/', views.create_customer, name='create_customer'),
    path('update/<int:pk>/', views.update_customer, name='update_customer'),
    path('detail/<int:pk>/', views.customer_detail, name='customer_detail'),
    path('detail/<int:customer_pk>/add_moto/', views.add_motorcycle, name='add_motorcycle'),
    path('toggle-status/<int:pk>/', views.toggle_customer_status, name='toggle_status'),
]
