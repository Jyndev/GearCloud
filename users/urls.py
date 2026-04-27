from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # Rutas de Gestión de Usuarios (CRUD Admin)
    path('management/', views.UserListView.as_view(), name='user_list'),
    path('create/', views.create_user, name='create_user'),
    path('update/<int:pk>/', views.update_user, name='update_user'),
    path('toggle/<int:pk>/', views.toggle_user_status, name='toggle_user'),
]
