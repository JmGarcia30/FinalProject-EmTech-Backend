from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Car


# -------- LIST --------
@login_required(login_url='login')
def car_list(request):
    # Optional: restrict further to staff only
    if not request.user.is_staff:
        return redirect('home')
    cars = Car.objects.all()
    return render(request, "cars/car_list.html", {"cars": cars})


# -------- CREATE --------
@login_required(login_url='login')
def car_create(request):
    if not request.user.is_staff:
        return redirect('home')
    if request.method == "POST":
        brand = request.POST.get("brand")
        model = request.POST.get("model")
        year = request.POST.get("year")
        plate = request.POST.get("plate_number")
        type = request.POST.get("type")
        status = request.POST.get("status")
        rate = request.POST.get("rental_rate_per_day")
        image = request.FILES.get("image")

        Car.objects.create(
            brand=brand,
            model=model,
            year=year,
            plate_number=plate,
            type=type,
            status=status,
            rental_rate_per_day=rate,
            image=image
        )

        return redirect("car_list")

    return render(request, "cars/car_create.html")
    

# -------- UPDATE --------
@login_required(login_url='login')
def car_update(request, id):
    car = get_object_or_404(Car, id=id)
    if not request.user.is_staff:
        return redirect('home')

    if request.method == "POST":
        car.brand = request.POST.get("brand")
        car.model = request.POST.get("model")
        car.year = request.POST.get("year")
        car.plate_number = request.POST.get("plate_number")
        car.type = request.POST.get("type")
        car.status = request.POST.get("status")
        car.rental_rate_per_day = request.POST.get("rental_rate_per_day")
        
        image = request.FILES.get("image")
        if image:
            car.image = image
        
        car.save()

        return redirect("car_list")

    return render(request, "cars/car_update.html", {"car": car})


# -------- DELETE --------
@login_required(login_url='login')
def car_delete(request, id):
    car = get_object_or_404(Car, id=id)
    if not request.user.is_staff:
        return redirect('home')

    if request.method == "POST":
        car.delete()
        return redirect("car_list")

    return render(request, "cars/car_delete.html", {"car": car})
