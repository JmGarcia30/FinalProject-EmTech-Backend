from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction 
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Car, Customer, RentalTransaction, RentalRequest 
from .serializers import CarSerializer, CustomerSerializer 
from decimal import Decimal 
from datetime import date 

# Simple check to see if the logged-in user is staff (required for admin views)
def is_staff_user(user):
    return user.is_staff

# --------------------------------------------------------------------------
# STAFF RENTAL MANAGEMENT VIEWS 
# These views handle approving, rejecting, and completing customer requests.
# --------------------------------------------------------------------------

@login_required(login_url='login')
@user_passes_test(is_staff_user)
def pending_requests_view(request):
    """
    Shows the staff a list of all rental requests waiting for approval.
    """
    # Grab all requests currently marked as 'PENDING'.
    pending_requests = RentalRequest.objects.filter(status='PENDING').select_related('car', 'customer').order_by('pickup_date')
        
    context = {
        'pending_requests': pending_requests
    }
    
    return render(request, 'cars/car_pending.html', context)

@login_required(login_url='login')
@user_passes_test(is_staff_user)
@transaction.atomic # Makes sure all database steps (request, transaction, car status) succeed or fail together.
def request_approve(request, request_id):
    """
    Approves a pending request, creates the final transaction record, 
    and updates the car's status to 'RENTED'.
    """
    if request.method == "POST": 
        # 1. Find the specific pending request.
        rental_request = get_object_or_404(RentalRequest, id=request_id, status='PENDING')
        car = rental_request.car 
        
        try:
            # Calculate the total duration in days.
            time_difference = rental_request.return_date - rental_request.pickup_date
            days = time_difference.days
            
            # Don't proceed if the dates are illogical (e.g., return before pickup).
            if days <= 0:
                print(f"Error: Invalid date range for Request ID {request_id}. Days: {days}")
                return redirect('pending_requests')
            
            # Safely calculate the total cost using Decimal to avoid floating point errors.
            rate = rental_request.car.rental_rate_per_day
            total_cost = Decimal(days) * Decimal(rate)
            
        except Exception as e:
            # If the calculation fails (e.g., rate is missing or badly formatted), log it and stop.
            print(f"Transaction Calculation Error for Request ID {request_id}: {e}")
            return redirect('pending_requests')

        # 2. Mark the original request as done/approved.
        rental_request.status = 'APPROVED'
        rental_request.save()
        
        # 3. Create the official RentalTransaction record.
        RentalTransaction.objects.create(
            car=car,
            customer=rental_request.customer,
            start_date=rental_request.pickup_date,
            end_date=rental_request.return_date,
            total_cost=total_cost, 
            status='ONGOING'
        )

        # 4. Take the car off the market by setting its status to RENTED.
        car.status = 'RENTED' 
        car.save()
        
        return redirect('pending_requests') 
        
    return redirect('pending_requests') 


@login_required(login_url='login')
@user_passes_test(is_staff_user)
def request_reject(request, request_id):
    """
    Rejects a pending request.
    """
    if request.method == "POST":
        # 1. Get the pending request.
        rental_request = get_object_or_404(RentalRequest, id=request_id, status='PENDING')
        
        # 2. Mark the request as rejected.
        rental_request.status = 'REJECTED'
        rental_request.save()
        
        return redirect('pending_requests')
        
    return redirect('pending_requests')


@login_required(login_url='login')
@user_passes_test(is_staff_user)
@transaction.atomic
def request_complete(request, transaction_id): 
    """
    Handles a completed rental: marks the transaction as finished and makes the car available again.
    """
    if request.method == "POST": 
        # Find the active transaction record.
        rental = get_object_or_404(RentalTransaction, id=transaction_id, status='ONGOING')
        
        # 1. Update the transaction status to COMPLETED.
        rental.status = 'COMPLETED'
        rental.save()
        
        # 2. Put the car back into the available pool.
        car = rental.car 
        car.status = 'AVAILABLE' 
        car.save()
        
        return redirect('car_list') 
        
    return redirect('car_list')

@login_required(login_url='login')
@user_passes_test(is_staff_user)
def active_rentals_view(request):
    """
    Staff view to list all current rentals (transactions marked 'ONGOING').
    """
    active_rentals = RentalTransaction.objects.filter(status='ONGOING').select_related('car', 'customer').order_by('end_date')
        
    context = {
        'active_rentals': active_rentals
    }
    
    return render(request, 'cars/car_active.html', context)

# --------------------------------------------------------------------------
# CAR CRUD VIEWS (CREATE, READ, UPDATE, DELETE)
# --------------------------------------------------------------------------

@login_required(login_url='login')
def car_list(request):
    if not request.user.is_staff:
        return redirect('home')
    # Show all cars to staff users.
    cars = Car.objects.all()
    return render(request, "cars/car_list.html", {"cars": cars})


@login_required(login_url='login')
def car_create(request):
    if not request.user.is_staff:
        return redirect('home')
    
    # Process the form submission to add a new car.
    if request.method == "POST":
        # Pull all standard and new fields from the submitted form data.
        brand = request.POST.get("brand")
        model = request.POST.get("model")
        year = request.POST.get("year")
        plate = request.POST.get("plate_number")
        type = request.POST.get("type")
        status = request.POST.get("status")
        rate = request.POST.get("rental_rate_per_day")
        image = request.FILES.get("image")

        # New Car detail fields.
        seats = request.POST.get("seats")
        fuel_type = request.POST.get("fuel_type")
        transmission = request.POST.get("transmission")
        color = request.POST.get("color")
        engine_size = request.POST.get("engine_size")
        mileage = request.POST.get("mileage")

        # Create and save the new Car object in one step.
        Car.objects.create(
            brand=brand,
            model=model,
            year=year,
            plate_number=plate,
            type=type,
            status=status,
            rental_rate_per_day=rate,
            image=image,
            seats=seats,
            fuel_type=fuel_type,
            transmission=transmission,
            color=color,
            engine_size=engine_size,
            mileage=mileage
        )

        return redirect("car_list")

    return render(request, "cars/car_create.html")


@login_required(login_url='login')
def car_update(request, id):
    # Fetch the car being edited.
    car = get_object_or_404(Car, id=id)
    if not request.user.is_staff:
        return redirect('home')

    if request.method == "POST":
        # Update fields with data from the submitted form.
        car.brand = request.POST.get("brand")
        car.model = request.POST.get("model")
        car.year = request.POST.get("year")
        car.plate_number = request.POST.get("plate_number")
        car.type = request.POST.get("type")
        
        # This line captures the new/current status from the form and fixes the defaulting issue.
        car.status = request.POST.get("status") 
        
        car.rental_rate_per_day = request.POST.get("rental_rate_per_day")
        
        # Update new detail fields.
        car.seats = request.POST.get("seats")
        car.fuel_type = request.POST.get("fuel_type")
        car.transmission = request.POST.get("transmission")
        car.color = request.POST.get("color")
        car.engine_size = request.POST.get("engine_size")
        car.mileage = request.POST.get("mileage")
        
        # Handle image upload, if a new file was provided.
        image = request.FILES.get("image")
        if image:
            car.image = image
        
        car.save()

        return redirect("car_list")

    # Display the form pre-filled with the current car data.
    return render(request, "cars/car_update.html", {"car": car})


@login_required(login_url='login')
def car_delete(request, id):
    # Find the car to delete.
    car = get_object_or_404(Car, id=id)
    if not request.user.is_staff:
        return redirect('home')

    # Delete the car after confirmation.
    if request.method == "POST":
        car.delete()
        return redirect("car_list")

    return render(request, "cars/car_delete.html", {"car": car})


# --------------------------------------------------------------------------
# MOBILE API VIEWS (Used by the mobile application)
# --------------------------------------------------------------------------

@api_view(['GET'])
def api_car_list(request):
    # Returns a list of all cars for the mobile app.
    cars = Car.objects.all()
    serializer = CarSerializer(cars, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@transaction.atomic
def api_submit_rental_request(request):
    """
    Handles rental request submissions from the mobile app.
    It either finds an existing customer by email or creates a new one, 
    then makes a PENDING RentalRequest entry.
    """
    data = request.data
    car_id = data.get('car_id')
    customer_data = data.get('customer_data', {})
    pickup_date = data.get('pickup_date')
    return_date = data.get('return_date')
    
    # 1. Ensure all essential fields are present in the request.
    if not all([car_id, customer_data, pickup_date, return_date, customer_data.get('license_number'), customer_data.get('email')]):
        return Response({'error': 'Missing required fields for rental request.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # 2. Verify the car exists.
        car = Car.objects.get(id=car_id)
        
        email = customer_data.get('email')
        license_number = customer_data.get('license_number')

        # 3. Find or Create the Customer. We rely on the email being unique.
        try:
            # A. Try to find the customer using their email.
            customer = Customer.objects.get(email=email)
            
            # If we find them, we update their details just in case they changed addresses or phone numbers.
            customer.license_number = license_number
            customer.first_name = customer_data.get('first_name', customer.first_name)
            customer.last_name = customer_data.get('last_name', customer.last_name)
            customer.phone = customer_data.get('phone', customer.phone)
            customer.address = customer_data.get('address', customer.address)
            customer.save()
            
        except Customer.DoesNotExist:
            # B. If no customer matches the email, create a completely new record for them.
            customer = Customer.objects.create(
                license_number=license_number,
                first_name=customer_data.get('first_name'),
                last_name=customer_data.get('last_name'),
                email=customer_data.get('email'),
                phone=customer_data.get('phone'),
                address=customer_data.get('address'),
                password='changepassword123', # Placeholder password for now.
            )
            
        # 4. Record the new rental request, setting its status to PENDING for staff review.
        RentalRequest.objects.create(
            car=car,
            customer=customer,
            pickup_date=pickup_date,
            return_date=return_date,
            status='PENDING' 
        )
        
        return Response({
            'message': 'Rental request submitted successfully for approval.',
            'request_id': customer.id 
        }, status=status.HTTP_201_CREATED)
        
    except Car.DoesNotExist:
        return Response({'error': 'Car not found.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        # Catch any other unexpected issues (e.g., date parsing errors).
        print(f"Error submitting rental request: {e}")
        return Response({'error': f'A server error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def api_customer_signup(request):
    """
    Handles creating a new customer account from the mobile app.
    """
    serializer = CustomerSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Account created successfully',
            'customer': serializer.data
        }, status=status.HTTP_201_CREATED)
    # If data validation fails, return the error details.
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def api_customer_login(request):
    """
    Validates a customer's login using email and password.
    """
    email = request.data.get('email')
    password = request.data.get('password')
    
    # Check if both fields were provided.
    if not email or not password:
        return Response({
            'error': 'Email and password are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Find the customer by email.
        customer = Customer.objects.get(email=email)
        
        # Check if the stored password matches the provided one.
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
        # If no customer matches the email.
        return Response({
            'error': 'Customer not found'
        }, status=status.HTTP_404_NOT_FOUND)