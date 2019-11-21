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
    return render(request, 'app/facility_detail.html', {'facility': facility})

def operator(request):
    return render(request, 'app/operator.html')

def driver(request):
    return render(request, 'app/driver.html', )

def admin(request):
    return render(request, 'app/admin.html')

def register(request):
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = CustomUserCreationForm(request.POST)

        #return redirect('../')

    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})

