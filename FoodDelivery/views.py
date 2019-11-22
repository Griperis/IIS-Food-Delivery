from django.shortcuts import render, redirect, get_object_or_404
from .models import CustomUser, Facility, Offer, Order, Item, Food, Drink
from .forms import CustomUserCreationForm, CustomUserChangeForm

from django.contrib.auth.forms import PasswordChangeForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout

def index(request):

    facilities = Facility.objects.all()

    return render(request, 'app/index.html', {"facilities":facilities})

def user_profile(request):
    user = request.user
    orders = Order.objects.all().filter(created_by = user)
    success = False


    if request.method == 'GET':
        success = "true" == request.GET.get("success",'')
        
        user_form = CustomUserChangeForm(initial={ 'username' : user.username, 'email' : user.email, 'first_name' : user.first_name, 'last_name' : user.last_name, 'address' : user.address, 'phone' : user.phone})
        password_form = PasswordChangeForm(user = user)

    return render(request, 'app/user_profile.html', {'orders' : orders, 'user_form' : user_form, 'password_form' : password_form, 'success' : success})

def edit_user(request):
    user = request.user
    #TODO: handle not registered user
    if request.method == 'POST':
        user_form = CustomUserChangeForm(request.POST, instance=request.user)
        if user_form.is_valid():
            #user.username = form.cleaned_data.get('username')
            user.email = user_form.cleaned_data.get('email')
            user.first_name = user_form.cleaned_data.get('first_name')
            user.last_name = user_form.cleaned_data.get('last_name')
            user.address = user_form.cleaned_data.get('address')
            user.phone = user_form.cleaned_data.get('phone')
            user.save()
            #TODO: vypsat že se to uložilo 
            #TODO: udelat username políčko aby nešlo editovat
        return redirect(to='/user?success=true')

def change_password(request):
    user = request.user
    #TODO: handle not registered user
    if request.method == 'POST':
        password_form = PasswordChangeForm(data=request.POST, user = user)
        if password_form.is_valid():
            new_password = password_form.cleaned_data.get('new_password1')
            user.set_password(new_password)
            user.save()

        return redirect(to='/login')

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

    return render(request, 'authentication/register.html', {'form': form})

def login_user(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username = username, password = password)
            if user is not None:
                login(request, user)
                return redirect(to = '/')
                #TODO: else vypsat něco
    else:
        form = AuthenticationForm()

    return render(request, 'authentication/login.html', {'form': form})

def logout_user(request):
    logout(request)
    return render(request, 'authentication/logged_out.html')