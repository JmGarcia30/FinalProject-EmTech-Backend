from django.db import models
from django.utils import timezone


class Car(models.Model):
    STATUS_CHOICES = [
        ("Available", "Available"),
        ("Rented", "Rented"),
        ("Maintenance", "Maintenance"),
    ]

    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.IntegerField()
    plate_number = models.CharField(max_length=20, unique=True)
    type = models.CharField(max_length=50)  # sedan, suv, van, etc.
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Available")
    rental_rate_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='cars/', blank=True, null=True)

    def __str__(self):
        return f"{self.brand} {self.model} ({self.plate_number})"


class Customer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255, default='changepassword123')
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    license_number = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class RentalTransaction(models.Model):
    STATUS_CHOICES = [
        ("Ongoing", "Ongoing"),
        ("Completed", "Completed"),
        ("Cancelled", "Cancelled"),
    ]

    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="rentals")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="rentals")
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField()
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Ongoing")

    def __str__(self):
        return f"Transaction {self.id} - {self.car.plate_number}"


class Payment(models.Model):
    transaction = models.ForeignKey(RentalTransaction, on_delete=models.CASCADE, related_name="payments")
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(default=timezone.now)
    method = models.CharField(max_length=50)  # Cash, GCash, Card, etc.

    def __str__(self):
        return f"Payment {self.id} for Transaction {self.transaction.id}"
