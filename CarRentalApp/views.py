from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Car, Customer
from .serializers import CarSerializer, CustomerSerializer


# -------- LIST --------
@login_required(login_url='login')
def car_list(request):
    # Optional: restrict further to staff only
    if not request.user.is_staff:
        return redirect('home')
    cars = Car.objects.all()
    return render(request, "cars/car_list.html", {"cars": cars})


# -------- CREATE --------
@login_required(login_url='login')
def car_create(request):
    if not request.user.is_staff:
        return redirect('home')
    if request.method == "POST":
        brand = request.POST.get("brand")
        model = request.POST.get("model")
        year = request.POST.get("year")
        plate = request.POST.get("plate_number")
        type = request.POST.get("type")
        status = request.POST.get("status")
        rate = request.POST.get("rental_rate_per_day")
        image = request.FILES.get("image")

        Car.objects.create(
            brand=brand,
            model=model,
            year=year,
            plate_number=plate,
            type=type,
            status=status,
            rental_rate_per_day=rate,
            image=image
        )

        return redirect("car_list")

    return render(request, "cars/car_create.html")
    

# -------- UPDATE --------
@login_required(login_url='login')
def car_update(request, id):
    car = get_object_or_404(Car, id=id)
    if not request.user.is_staff:
        return redirect('home')

    if request.method == "POST":
        car.brand = request.POST.get("brand")
        car.model = request.POST.get("model")
        car.year = request.POST.get("year")
        car.plate_number = request.POST.get("plate_number")
        car.type = request.POST.get("type")
        car.status = request.POST.get("status")
        car.rental_rate_per_day = request.POST.get("rental_rate_per_day")
        
        image = request.FILES.get("image")
        if image:
            car.image = image
        
        car.save()

        return redirect("car_list")

    return render(request, "cars/car_update.html", {"car": car})


# -------- DELETE --------
@login_required(login_url='login')
def car_delete(request, id):
    car = get_object_or_404(Car, id=id)
    if not request.user.is_staff:
        return redirect('home')

    if request.method == "POST":
        car.delete()
        return redirect("car_list")

    return render(request, "cars/car_delete.html", {"car": car})


# -------- API VIEW FOR CAR LISTING --------
@api_view(['GET'])
def api_car_list(request):
    cars = Car.objects.all()
    serializer = CarSerializer(cars, many=True)
    return Response(serializer.data)


# -------- API VIEW FOR CUSTOMER SIGNUP --------
@api_view(['POST'])
def api_customer_signup(request):
    """
    Create a new customer account
    Expected fields: first_name, last_name, email, password, phone, address, license_number
    """
    serializer = CustomerSerializer(data=request.data)
    if serializer.is_valid():
        # Password will be stored as plain text (for simple implementation)
        # In production, use proper password hashing
        serializer.save()
        return Response({
            'message': 'Account created successfully',
            'customer': serializer.data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -------- API VIEW FOR CUSTOMER LOGIN/CHECK --------
@api_view(['POST'])
def api_customer_login(request):
    """
    Validate customer login with email and password
    Expected fields: email, password
    """
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not email or not password:
        return Response({
            'error': 'Email and password are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        customer = Customer.objects.get(email=email)
        
        # Check if password matches
        if customer.password == password:
            serializer = CustomerSerializer(customer)
            return Response({
                'message': 'Login successful',
                'customer': serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Invalid password'
            }, status=status.HTTP_401_UNAUTHORIZED)
            
    except Customer.DoesNotExist:
        return Response({
            'error': 'Customer not found'
        }, status=status.HTTP_404_NOT_FOUND)
