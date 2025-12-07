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

    seats = models.IntegerField(
        default=5,
        help_text="Number of seats in the vehicle."
    )
    fuel_type = models.CharField(
        max_length=50,
        default="Gasoline",
        blank=True, 
        null=True
    )
    transmission = models.CharField(
        max_length=50,
        default="Automatic",
        blank=True,
        null=True
    )
    color = models.CharField(
        max_length=50,
        default="White",
        blank=True,
        null=True
    )
    engine_size = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="e.g., '1.5L' or 'V6'"
    )
    mileage = models.IntegerField(
        default=0,
        help_text="Odometer reading in kilometers."
    )

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
    method = models.CharField(max_length=50) 

    def __str__(self):
        return f"Payment {self.id} for Transaction {self.transaction.id}"
    


class RentalRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed'),
    ]

    car = models.ForeignKey(
        'Car', 
        on_delete=models.PROTECT, 
        related_name='rental_requests',
        help_text="The car being requested for rental."
    )
    customer = models.ForeignKey(
        'Customer', 
        on_delete=models.PROTECT, 
        related_name='customer_requests',
        help_text="The customer who placed the request."
    )
    request_date = models.DateTimeField(
        default=timezone.now,
        help_text="The date and time the request was submitted."
    )
    pickup_date = models.DateField()
    return_date = models.DateField()
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='PENDING',
        help_text="Current status of the rental request."
    )

    def __str__(self):
        return f"Request for {self.car.brand} {self.car.model} by {self.customer.first_name} ({self.status})"


class Notification(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='notifications')
    rental_request = models.ForeignKey(RentalRequest, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.customer.email} - {self.title}"