from django.urls import path
from . import views

urlpatterns = [
    path('cars/', views.car_list, name='car_list'),
    path('cars/add/', views.car_create, name='car_create'),
    path('cars/<int:id>/edit/', views.car_update, name='car_update'),
    path('cars/<int:id>/delete/', views.car_delete, name='car_delete'),
]
