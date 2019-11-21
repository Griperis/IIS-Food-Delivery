from django.shortcuts import render, redirect, get_object_or_404
from .models import CustomUser, Facility, Offer, Order, Item, Food, Drink
from .forms import CustomUserCreationForm

def index(request):

    facilities = Facility.objects.all()

    return render(request, 'app/index.html', {"facilities":facilities})

def user_profile(request):
    return render(request, 'app/user_profile.html')


def facility_detail(request, facility_id):
    facility = get_object_or_404(Facility, pk=facility_id)
    return render(request, 'app/facility/facility_detail.html', {'facility': facility})

def operator(request):
    return render(request, 'app/operator.html')

def driver(request):
    return render(request, 'app/driver.html', )

def admin(request):
    return render(request, 'app/admin.html')

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

    return render(request, 'registration/register.html', {'form': form})

