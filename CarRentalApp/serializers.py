from rest_framework import serializers
from .models import Car, Customer, RentalTransaction, Payment
from django.db import transaction

# --------------------------------------------------------------------------
# CORE DATA SERIALIZERS (Standard CRUD and Staff Management)
# --------------------------------------------------------------------------

class CarSerializer(serializers.ModelSerializer):
    """Serializer for the Car model, used for inventory and API listings."""
    class Meta:
        model = Car
        fields = [
            'id', 
            'brand', 
            'model', 
            'year', 
            'plate_number', 
            'type', 
            'status', 
            'rental_rate_per_day', 
            'image',
            'seats',
            'fuel_type',
            'transmission',
            'color',
            'engine_size',
            'mileage'
        ]


class CustomerSerializer(serializers.ModelSerializer):
    """Serializer for Customer data, used for staff management and sign-up/login (handles password)."""
    password = serializers.CharField(write_only=True, required=True, min_length=6)
    
    class Meta:
        model = Customer
        fields = ['id', 'first_name', 'last_name', 'email', 'password', 'phone', 
                  'address', 'license_number'] 
        extra_kwargs = {'password': {'write_only': True}}
        

# --------------------------------------------------------------------------
# MOBILE RENTAL SUBMISSION SERIALIZERS (Nested Logic)
# --------------------------------------------------------------------------

class CustomerSubmissionSerializer(serializers.ModelSerializer):
    """A simplified serializer used specifically to parse nested customer details within a rental request."""
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'license_number']


class RentalRequestSubmissionSerializer(serializers.ModelSerializer):
    """
    Main serializer for handling mobile app requests. It includes nested customer data,
    validates the car ID, and enforces the creation of a 'PENDING' transaction.
    """
    customer = CustomerSubmissionSerializer() 
    car_id = serializers.IntegerField(write_only=True) 

    class Meta:
        model = RentalTransaction
        fields = ['id', 'car_id', 'customer', 'start_date', 'end_date', 'total_cost']
        read_only_fields = ['id', 'status'] 

    def create(self, validated_data):
        with transaction.atomic():
            customer_data = validated_data.pop('customer')
            car_id = validated_data.pop('car_id')
            
            # Handle Customer: Get existing or create new
            customer_instance, created = Customer.objects.get_or_create(
                email=customer_data.get('email'),
                defaults={
                    'license_number': customer_data.get('license_number'),
                    'password': 'N/A', 
                    **customer_data
                }
            )

            # Get Car Instance
            try:
                car_instance = Car.objects.get(id=car_id)
            except Car.DoesNotExist:
                raise serializers.ValidationError({"car_id": "Car with this ID does not exist."})
                
            # Create the RentalTransaction
            rental = RentalTransaction.objects.create(
                car=car_instance,
                customer=customer_instance,
                status='PENDING',
                **validated_data
            )
            return rental

# --------------------------------------------------------------------------
# TRANSACTION & PAYMENT SERIALIZERS (Cross-Reference Detail)
# --------------------------------------------------------------------------

class RentalTransactionSerializer(serializers.ModelSerializer):
    """Serializer for full transaction details, including related Car and Customer objects."""
    car = CarSerializer(read_only=True)
    customer = CustomerSerializer(read_only=True)
    car_id = serializers.IntegerField(write_only=True)
    customer_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = RentalTransaction
        fields = ['id', 'car', 'customer', 'car_id', 'customer_id', 
                  'start_date', 'end_date', 'total_cost', 'status']


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for payment records, linking to the relevant transaction."""
    transaction = RentalTransactionSerializer(read_only=True)
    transaction_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Payment
        fields = ['id', 'transaction', 'transaction_id', 'amount_paid', 
                  'payment_date', 'method']