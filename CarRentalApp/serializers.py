from rest_framework import serializers
from .models import Car, Customer, RentalTransaction, Payment


class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = ['id', 'brand', 'model', 'year', 'plate_number', 'type', 
                  'status', 'rental_rate_per_day', 'image']


class CustomerSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=6)
    
    class Meta:
        model = Customer
        fields = ['id', 'first_name', 'last_name', 'email', 'password', 'phone', 
                  'address']
        extra_kwargs = {'password': {'write_only': True}}


class RentalTransactionSerializer(serializers.ModelSerializer):
    car = CarSerializer(read_only=True)
    customer = CustomerSerializer(read_only=True)
    car_id = serializers.IntegerField(write_only=True)
    customer_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = RentalTransaction
        fields = ['id', 'car', 'customer', 'car_id', 'customer_id', 
                  'start_date', 'end_date', 'total_cost', 'status']


class PaymentSerializer(serializers.ModelSerializer):
    transaction = RentalTransactionSerializer(read_only=True)
    transaction_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Payment
        fields = ['id', 'transaction', 'transaction_id', 'amount_paid', 
                  'payment_date', 'method']
