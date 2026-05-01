from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    path('', views.billing_list, name='billing_list'),
    path('crear/', views.invoice_create, name='invoice_create'),
    path('<int:pk>/', views.invoice_detail, name='invoice_detail'),
    path('<int:pk>/pagar/', views.register_payment, name='register_payment'),
    path('liquidar-comisiones/<int:user_id>/', views.settle_commissions, name='settle_commissions'),
]
