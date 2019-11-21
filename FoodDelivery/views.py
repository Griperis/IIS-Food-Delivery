from django.shortcuts import render, redirect
from .models import CustomUser, Facility, Offer, Order, Item, Food, Drink
from .forms import CustomUserCreationForm

def index(request):

    facilities = Facility.objects.all()

    return render(request, 'FoodDelivery/index.html', {"facilities":facilities})

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        
        if form.is_valid():

            new_username = form.cleaned_data.get('username')
            new_email = form.cleaned_data.get('email')
            new_first_name = form.cleaned_data.get('first_name')
            new_last_name = form.cleaned_data.get('last_name')
            new_address = form.cleaned_data.get('address')
            new_phone = form.cleaned_data.get('phone')
            new_password = form.cleaned_data.get('password1')

            new_user = CustomUser(username = new_username, email = new_email, first_name = new_first_name, last_name = new_last_name, address = new_address, phone = new_phone, password = new_password)
            new_user.save()
            
            return redirect(to = 'login')

    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {"form":form})
