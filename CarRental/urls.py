# File: CarRental/urls.py (Project Level)

"""
... (The existing comments) ...
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from CarRental import views
from CarRentalApp import views as app_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_page, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    #  EXISTING API PATHS 
    path('api/cars/', app_views.api_car_list, name='api_car_list'),
    path('api/customers/signup/', app_views.api_customer_signup, name='api_customer_signup'),
    path('api/customers/login/', app_views.api_customer_login, name='api_customer_login'),
    
    #  NEW CRITICAL API PATHS ADDED HERE 
    path('api/submit-rental-request/', app_views.api_submit_rental_request, name='api_submit_rental_request'),
    path('api/create-rental-transaction/', app_views.api_create_rental_transaction, name='api_create_rental_transaction'),
    path('api/submit-payment/', app_views.api_submit_payment, name='api_submit_payment'),
    path('api/notifications/', app_views.api_get_notifications, name='api_get_notifications'),
    path('api/notifications/mark-read/', app_views.api_mark_notification_read, name='api_mark_notification_read'),
    
    #  INCLUDE APP URLS (Staff views and CRUD) 
    path('cars/', include('CarRentalApp.urls')),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)