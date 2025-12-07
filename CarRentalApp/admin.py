from django.contrib import admin

from CarRentalApp.models import Car, Customer, Payment, RentalTransaction, RentalRequest, Notification

# Register your models here.
admin.site.register(Car)
admin.site.register(Customer)
admin.site.register(RentalTransaction)
admin.site.register(Payment)
admin.site.register(RentalRequest)
admin.site.register(Notification)