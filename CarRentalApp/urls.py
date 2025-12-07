# File: CarRentalApp/urls.py (Application Level)

from django.urls import path
from . import views

urlpatterns = [
    path('cars/', views.car_list, name='car_list'),
    path('cars/add/', views.car_create, name='car_create'),
    path('cars/<int:id>/edit/', views.car_update, name='car_update'),
    path('cars/<int:id>/delete/', views.car_delete, name='car_delete'),
    
    # Staff Request Management
    path('rentals/pending/', views.pending_requests_view, name='pending_requests'),
    path('rentals/approve/<int:request_id>/', views.request_approve, name='request_approve'),
    path('rentals/reject/<int:request_id>/', views.request_reject, name='request_reject'),
    
    # NEW STAFF ACTIVE RENTALS MANAGEMENT 
    path('rentals/active/', views.active_rentals_view, name='active_rentals'), 
    path('rentals/complete/<int:transaction_id>/', views.request_complete, name='request_complete'),
    
    # API ENDPOINTS FOR MOBILE APP
    path('api/cars/', views.api_car_list, name='api_car_list'),
    path('api/submit-rental-request/', views.api_submit_rental_request, name='api_submit_rental_request'),
    path('api/customers/signup/', views.api_customer_signup, name='api_customer_signup'),
    path('api/customers/login/', views.api_customer_login, name='api_customer_login'),
    path('api/create-rental-transaction/', views.api_create_rental_transaction, name='api_create_rental_transaction'),
    path('api/submit-payment/', views.api_submit_payment, name='api_submit_payment'),
]