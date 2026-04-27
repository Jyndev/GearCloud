from django.contrib.auth.decorators import login_required
from customers.models import Customer, Motorcycle

from django.shortcuts import render

@login_required
def index(request):
    total_customers = Customer.objects.count()
    total_motos = Motorcycle.objects.count()
    
    return render(request, 'dashboard/index.html', {
        'total_customers': total_customers,
        'total_motos': total_motos,
    })
