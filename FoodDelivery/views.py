from django.shortcuts import render, redirect, get_object_or_404

from .models import CustomUser, Facility, Offer, Order, Item, Food, Drink, OrderItem
from .forms import CustomUserCreationForm, CustomUserChangeForm, FacilityChangeForm
from django.contrib.auth.forms import PasswordChangeForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout

from datetime import date, datetime, timedelta
from django.utils import timezone

def index(request):

    facilities = Facility.objects.all()

    return render(request, 'app/index.html', {'facilities':facilities})

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
    #TODO: handle not registered user
    if request.method == 'POST':
        password_form = PasswordChangeForm(data=request.POST, user = user)
        if password_form.is_valid():
            new_password = password_form.cleaned_data.get('new_password1')
            user.set_password(new_password)
            user.save()

        return redirect(to='/login')

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
    #set default values
    facility_form = FacilityChangeForm()
    selected_facility = None
    facility_deleted = '-1'
    facility_changed = '-1'
    new_facility = '-1'

    if request.method == 'GET':
        name = request.GET.get('selected_facility', '')
        facility_deleted = request.GET.get('facility_deleted', '')
        facility_changed = request.GET.get('facility_changed', '')
        new_facility = request.GET.get('new_facility', '')

        if name != '':
            selected_facility = Facility.objects.get(name = name)
            facility_form = FacilityChangeForm(initial={ 'name' : selected_facility.name, 'address' : selected_facility.address, 'opening_time': selected_facility.opening_time,
                                                    'closing_time' : selected_facility.closing_time, 'state' : selected_facility.state, }) #'offers' : selected_fac.offers })


    if request.method == 'POST':
        fac_form = FacilityChangeForm(request.POST, instance=request.user)

    #send data
    context = { 'user' : request.user,
                'facilities' : Facility.objects.all(),
                'selected_facility' : selected_facility,
                'facility_deleted' : facility_deleted,
                'facility_changed' : facility_changed,
                'new_facility' : new_facility, 
                'fac_form' : facility_form, }
    return render(request, 'app/operator.html', context)

def create_facility(request):
    code = '1'
    if request.method == 'POST':
        next_url = request.POST.get('next_url', '/')
        new_name = request.POST.get('new_facility_name')
        new_address = request.POST.get('new_facility_address')

        print(new_name)
        print(new_address)

        new_facility = Facility(name=new_name, address=new_address, opening_time=timezone.now(), closing_time=timezone.now(), state='D')
        
        #try:
        new_facility.save()
        print('OK')
        code = '0'
    #except Exception:
    #    print('fail')
    #    code = '2'

    return redirect(to = next_url + '?new_facility=' + code)

def edit_facility(request):
    next_url = request.POST.get('next_url')
    name = request.POST.get('name')

    if name != None:
        facility = Facility.objects.get(name = name)

    if facility != None:
        if request.method == 'POST':
            facility_form = FacilityChangeForm(request.POST, instance = request.user)

            if facility_form.is_valid():
                code = 0

                facility.address = facility_form.cleaned_data.get('address')
                facility.opening_time = facility_form.cleaned_data.get('opening_time')
                facility.closing_time = facility_form.cleaned_data.get('closing_time')
                facility.state = facility_form.cleaned_data.get('state')
                facility.save()
            else:
                code = 1
        
            return redirect(to = next_url + '&facility_changed=' + code)

def delete_facility(request):
    next_url = request.POST.get('next_url')
    name = request.POST.get('name', '')

    code = '1'
    if name != '':
        facility_to_delete = Facility.objects.get(name='name')
        facility_to_delete.delete()
        code = '0'

    return redirect(to = next_url + '?facility_deleted=' + code)

def driver(request):
    context = { 'orders' : Order.objects.filter(handled_by=request.user.id).order_by('-date')[::-1],
                'facilities' : Facility.objects.all(),
                'user' : request.user, 
                'filter_state' : 'all',
                'filter_facility' : 'all', 
                'filter_date' : str(date.today()), }

    if request.method == 'POST':
        #get and save status of page
        val = request.GET.get('filter_state')
        if val != None and val != '':
            context['filter_state'] = val
        val = request.GET.get('filter_facility')
        if val != None and val != '':
            context['filter_facility'] = request.GET.get('filter_facility')
        if val != None and val != '':
            context['filter_date'] = request.GET.get('filter_date')

        order_id = request.POST.get('order_id')
        if order_id != None:
            order = get_object_or_404(Order, pk=order_id)
            order.state = 'F'
            order.save()
    elif request.method == 'GET':
        #get and save status of page
        filter_state = request.GET.get('filter_state')
        if filter_state == None or filter_state == '':
            filter_state = 'all'
        context['filter_state'] = filter_state
        filter_facility = request.GET.get('filter_facility')
        if filter_facility == None or filter_facility == '':
            filter_facility = 'all'
        context['filter_facility'] = filter_facility
        filter_date = request.GET.get('filter_date')
        if filter_date == None or filter_date == '':
            filter_date = str(date.today())
        context['filter_date'] = filter_date
        
        end_date = datetime.strptime(filter_date, '%Y-%m-%d') + timedelta(days=1)
        #use filters to show orders
        if filter_facility == 'all':
            if filter_state == 'all':
                context['orders'] = Order.objects.filter(date__gte=filter_date,
                                                        date__lt=end_date,
                                                        handled_by=request.user.id).order_by('-date')[::-1]
            else:
                context['orders'] = Order.objects.filter(state=filter_state, 
                                                        date__gte=filter_date,
                                                        date__lte=end_date, 
                                                        handled_by=request.user.id).order_by('-date')[::-1]
        else:
            if filter_state == 'all':
                context['orders'] = Order.objects.filter(belongs_to=filter_facility, 
                                                        date__gte=filter_date,
                                                        date__lte=end_date, 
                                                        handled_by=request.user.id).order_by('-date')[::-1]
            else:
                context['orders'] = Order.objects.filter(state=filter_state, 
                                                        belongs_to=filter_facility,
                                                        date__gte=filter_date,
                                                        date__lte=end_date, 
                                                        handled_by=request.user.id).order_by('-date')[::-1]

    #convert string representation of facility_id to integer representation
    if context['filter_facility'] != 'all':
        context['filter_facility'] = int(context['filter_facility'])

    return render(request, 'app/driver.html', context)

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
            #TODO: kontrolovat formát tel. čísla
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