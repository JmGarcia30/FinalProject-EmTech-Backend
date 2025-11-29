from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse


def home_page(request):
    return render(request, "home_page.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            # Redirect to cars list instead of admin panel
            return redirect(reverse("car_list"))
        messages.error(request, "Invalid credentials or not authorized.")
    return render(request, "login.html")


def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect("home")
