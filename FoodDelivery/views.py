from django.shortcuts import render, redirect, get_object_or_404, HttpResponse, loader, HttpResponseRedirect, reverse
from .models import CustomUser, Facility, Offer, Order, Item, Food, Drink, OrderItem
from .forms import CustomUserCreationForm, CustomUserChangeForm, CustomPasswordChangeForm, CustomAuthenticationForm
from django.contrib.auth import authenticate, login, logout

import datetime
from .cookies import *

def index(request):

    facilities = Facility.objects.all()

    return render(request, 'app/index.html', {'facilities': facilities})

def user_profile(request):
    user = request.user
    orders = Order.objects.all().filter(created_by = user)
    orders_with_data = []

    success = -1
    pwdsuccess = -1
    goto_info = False

    for order in orders:
        items = OrderItem.objects.all().filter(order = order)
        order_data = {"order" : order, "items" : items}
        orders_with_data.append(order_data)
    
    orders_with_data.reverse()

    if request.method == 'GET':
        if request.GET.get("success",'') == "1":
            success = 1
        if request.GET.get("success",'') == "0":
            success = 0
        if request.GET.get("pwdsuccess",'') == "1":
            pwdsuccess = 1
        if request.GET.get("pwdsuccess",'') == "0":
            pwdsuccess = 0
        
        if request.GET.get("tab",'') == "info":
            goto_info = True

        user_form = CustomUserChangeForm(initial={ 'username' : user.username, 'email' : user.email, 'first_name' : user.first_name, 'last_name' : user.last_name, 'address' : user.address, 'phone' : user.phone})
        password_form = CustomPasswordChangeForm(user = user)

    return render(request, 'app/user_profile.html', {'orders_with_data' : orders_with_data, 'user_form' : user_form, 'password_form' : password_form, 'success' : success, 'pwdsuccess' : pwdsuccess, 'goto_info' : goto_info})

def edit_user(request):
    user = request.user
    if user != None:
        if request.method == 'POST':
            user_form = CustomUserChangeForm(request.POST, instance=request.user)
            if user_form.is_valid():
                user.email = user_form.cleaned_data.get('email')
                user.first_name = user_form.cleaned_data.get('first_name')
                user.last_name = user_form.cleaned_data.get('last_name')
                user.address = user_form.cleaned_data.get('address')
                user.phone = user_form.cleaned_data.get('phone')
                user.save()
                return redirect(to='/user?success=1&tab=info')
            return redirect(to='/user?success=0&tab=info')

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
            return redirect(to='/user?pwdsuccess=0&tab=info')

def filter_offers(facility, filter_form):
    search_field = filter_form['search']
    type_field = filter_form['type']
    offers = facility.offers.all()
    filtered_offers = {}
    for offer in offers:
        if search_field != '':
            if type_field == 'type':
                filtered_items = offer.items.filter(variant__contains=search_field)
            else:
                filtered_items = offer.items.filter(name__contains=search_field)
        else:
            filtered_items = offer.items.all()
        filtered_offers[offer.pk] = {'items': filtered_items, 'name': offer.name, 'variant': offer.variant}
    return filtered_offers

def create_new_order(order_state, facility_id, user):
    facility = get_object_or_404(Facility, pk=facility_id)
    order_items = order_state['order']
    price = order_state['price']
    new_order = Order(state='A', price=price, belongs_to=facility)
    if user.is_authenticated:
        new_order.created_by = user
    new_order.save()
    for entry in order_items:
        oi = OrderItem(item=entry['item'], order=new_order, count=entry['count'])
        oi.save()
        new_order.items.add(entry['item'])
    
    return new_order.pk

def is_fac_open(facility):
    if facility.opening_time == facility.closing_time:
        return True
    now = datetime.datetime.now().time()
    if facility.opening_time < now:
        return facility.opening_time <= now < facility.closing_time
    else:
        return facility.opening_time <= now or now <= facility.closing_time

def facility_detail(request, facility_id):
    if request.method == 'POST':
        order_state = load_order_state(request, str(facility_id))
        order_id = create_new_order(order_state, facility_id, request.user)
        response = redirect('order_summary', order_id)
        remove_order_cookies(response)
        return response
    else:
        facility = get_object_or_404(Facility, pk=facility_id)

        search_field = ''
        type_field = ''

        if request.GET.get('search'):
            search_field = request.GET['search']
        if request.GET.get('filter_type'):
            type_field = request.GET['filter_type']
        
        if search_field == '':
            filter_form = load_form_state(request)
        else:
            filter_form = {'search': search_field, 'type': type_field}

        if request.GET.get('submit'):
            if request.GET['submit'] == 'remove_filter':
                filter_form = {'type': '', 'search': ''}
        filtered_offers = filter_offers(facility, filter_form)

        is_open = is_fac_open(facility)
        context = {'facility': facility, 'offers': filtered_offers, 'can_order': True, 'summary': {}, 'search_form': filter_form }

        order_summary = load_order_state(request, str(facility_id))
        if request.GET.get('add_item'):
            added_item_id = request.GET['add_item']
            order_summary = add_order_item(request, added_item_id, str(facility_id))
        elif request.GET.get('remove_item'):
            removed_item_id = request.GET['remove_item']
            order_summary = remove_order_item(request, removed_item_id, str(facility_id))

        if len(order_summary['order']) == 0:
            context['can_order'] = False

        if facility.state == 'D' or not is_open:
            context['can_order'] = False

        context['summary'] = order_summary
        response = render(request, 'app/facility_detail.html', context)
        if (order_summary):
            save_order_state(response, order_summary['order'], str(facility_id))

        if request.GET.get('submit'):
            if request.GET['submit'] == 'remove_filter':
                remove_form_state(response)
            else:
                save_form_state(response, filter_form)
        return response

def order_summary(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    order_items = OrderItem.objects.all().filter(order=order_id)
    order_data = {'order': order, 'items': order_items }
    return render(request, 'app/order_summary.html', { 'order_data': order_data })

def operator(request, driver_id):
    return render(request, 'app/operator.html')

def driver(request):
    context = { 'orders' : Order.objects.all().order_by('-date')[::-1],
                'facilities' : Facility.objects.all(),
                'user' : request.user, 
                'filter_state' : 'all',
                'filter_facility' : 'all', 
                'filter_date' : str(datetime.date.today()), }

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
            filter_date = str(datetime.date.today())
        context['filter_date'] = filter_date
        
        end_date = datetime.datetime.strptime(filter_date, '%Y-%m-%d') + datetime.timedelta(days=1)
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

    next = request.GET.get('next', '/')
    user_exists = False

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

            new_user = CustomUser(username = new_username, email = new_email, first_name = new_first_name, last_name = new_last_name, address = new_address, phone = new_phone)
            new_user.set_password(new_password)
            try:
                new_user.save()
                user = authenticate(username = new_username, password = new_password)
                login(request, user)
                return redirect(to = next)
            
            except Exception:
                user_exists = True           
    else:
        form = CustomUserCreationForm()

    return render(request, 'authentication/register.html', {'form': form, 'user_exists': user_exists})

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

def aws_debug(request):
    items = Item.objects.all()
    return render(request, 'app/aws_debug.html', {'items': items })