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
    
    #  INCLUDE APP URLS (Staff views and CRUD) 
    path('cars/', include('CarRentalApp.urls')),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)