from django.shortcuts import render, redirect, get_object_or_404

from .models import CustomUser, Facility, Offer, Order, Item, Food, Drink, OrderItem
from .forms import CustomUserCreationForm, CustomUserChangeForm, CustomPasswordChangeForm, CustomAuthenticationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout


def index(request):

    facilities = Facility.objects.all()

    return render(request, 'app/index.html', {'facilities':facilities})

def user_profile(request):
    user = request.user
    orders = Order.objects.all().filter(created_by = user)
    orders_with_data = []

    for order in orders:
        items = OrderItem.objects.all().filter(order = order)
        order_data = {"order" : order, "items" : items}
        orders_with_data.append(order_data)
    
    orders_with_data.reverse()

    success = False
    pwderror = False

    if request.method == 'GET':
        success = "true" == request.GET.get("success",'')
        pwderror = "true" == request.GET.get("pwderror",'')
        
        user_form = CustomUserChangeForm(initial={ 'username' : user.username, 'email' : user.email, 'first_name' : user.first_name, 'last_name' : user.last_name, 'address' : user.address, 'phone' : user.phone})
        password_form = CustomPasswordChangeForm(user = user)

    return render(request, 'app/user_profile.html', {'orders_with_data' : orders_with_data, 'user_form' : user_form, 'password_form' : password_form, 'success' : success, 'pwderror' : pwderror})

def edit_user(request):
    user = request.user
    #TODO: handle not registered user
    if request.method == 'POST':
        user_form = CustomUserChangeForm(request.POST, instance=request.user)
        if user_form.is_valid():
            user.email = user_form.cleaned_data.get('email')
            user.first_name = user_form.cleaned_data.get('first_name')
            user.last_name = user_form.cleaned_data.get('last_name')
            user.address = user_form.cleaned_data.get('address')
            user.phone = user_form.cleaned_data.get('phone')
            #TODO: kontrolovat formát tel. čísla
            user.save()
            return redirect(to='/user?success=true')
        #TODO: mozna dalši return?

def change_password(request):
    user = request.user
    if user != None:
        if request.method == 'POST':
            password_form = CustomPasswordChangeForm(data=request.POST, user = user)
            if password_form.is_valid():
                new_password = password_form.cleaned_data.get('new_password1')
                user.set_password(new_password)
                user.save()
                return redirect(to='/login')
            return redirect(to='/user?pwderror=true')

def facility_detail(request, facility_id):
    if request.method == 'POST':
        form_values = request.POST.dict().items()
        item_count = {}
        total_price = 0
        for input_name, value in form_values:
            if input_name == 'csrfmiddlewaretoken' or value == 0:
                continue
            offer, item_id = input_name.split(';')
            if item_id in item_count:
                item_count[item_id] += value
            else:
                item_count[item_id] = value

        facility = Facility.objects.get(pk=facility_id)
        new_order = Order(state=Order.ORDER_STATE[0], price=total_price, belongs_to=facility, created_by=request.user)
        new_order.save()
        
        items = []
        for item_id, count in item_count.items():
            item = Item.objects.get(pk=item_id)
            new_oi = OrderItem(item=item, order=new_order, count=count)
            new_oi.save()
            items.append(item)

        new_order.items.add(*items)

        return redirect(to='user_profile')
    else:
        facility = get_object_or_404(Facility, pk=facility_id)
        return render(request, 'app/facility/facility_detail.html', {'facility': facility})

def operator(request):
    return render(request, 'app/operator.html')

def driver(request):
    return render(request, 'app/driver.html', )

def admin(request):
    return render(request, 'app/admin.html')

def register(request):
    next = request.GET.get('next', '/')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        
        if form.is_valid():
            new_username = form.cleaned_data.get('username')
            new_email = form.cleaned_data.get('email')
            new_first_name = form.cleaned_data.get('first_name')
            new_last_name = form.cleaned_data.get('last_name')
            new_address = form.cleaned_data.get('address')
            new_phone = form.cleaned_data.get('phone')
            #TODO: kontrolovat formát tel. čísla
            #TODO: ošetřit pokud jsou špatné údaje
            new_password = form.cleaned_data.get('password1')

            new_user = CustomUser(username = new_username, email = new_email, first_name = new_first_name, last_name = new_last_name, address = new_address, phone = new_phone)
            new_user.set_password(new_password)
            new_user.save()
            
            user = authenticate(username = new_username, password = new_password)
            if user is not None:
                login(request, user)

            return redirect(to = next)
        #TODO: else?
    else:
        form = CustomUserCreationForm()

    return render(request, 'authentication/register.html', {'form': form})

def login_user(request):
    next = request.GET.get('next', '/')
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username = username, password = password)
            if user is not None:
                login(request, user)
                return redirect(to = next)
    else:
        form = CustomAuthenticationForm()

    return render(request, 'authentication/login.html', {'form': form})

def logout_user(request):
    logout(request)
    return render(request, 'authentication/logged_out.html')