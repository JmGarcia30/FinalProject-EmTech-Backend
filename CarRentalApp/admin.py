from django.contrib import admin

from CarRentalApp.models import Car, Customer, Payment, RentalTransaction

# Register your models here.
admin.site.register(Car)
admin.site.register(Customer)
admin.site.register(RentalTransaction)
admin.site.register(Payment)