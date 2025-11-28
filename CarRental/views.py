#For my Django Car Rental System

from django.shortcuts import render
from CarRentalApp.models import Car

def home_page(request):
    return render(request, "home_page.html")
