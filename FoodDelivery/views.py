from django.shortcuts import render, redirect
from .models import CustomUser, Facility, Offer, Order, Item, Food, Drink
from .forms import CustomUserCreationForm ,FacilityForm

def index(request):

    facilities = Facility.objects.all()

    return render(request, 'FoodDelivery/index.html', {"facilities":facilities})

def register(request):
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = CustomUserCreationForm(request.POST)

        #return redirect('../')

    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {"form":form})
