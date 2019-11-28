from django.shortcuts import render, redirect, get_object_or_404, HttpResponse, loader, HttpResponseRedirect, reverse
from .models import CustomUser, Facility, Offer, Order, Item, Food, Drink, OrderItem
from .forms import CustomUserCreationForm, CustomUserChangeForm, CustomPasswordChangeForm, CustomAuthenticationForm, FacilityChangeForm, OfferChangeForm, FoodChangeForm, DrinkChangeForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from django.utils import timezone

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
    next_url = request.POST.get('next_url')
    selected_user = request.POST.get('selected_user')

    if selected_user == '':
        return redirect(to=next_url)
    if selected_user != None:
        user = CustomUser.objects.get(username = selected_user)
    else:
        user = request.user

    if user != None:
        if request.method == 'POST':
            
            driver_group = Group.objects.get(name='Driver')
            operator_group = Group.objects.get(name='Operator')
            admin_group = Group.objects.get(name='Administrator')

            user.groups.clear()
            if request.POST.get("permissions_select") == '1':
                user.groups.add(driver_group, operator_group, admin_group)
            if request.POST.get("permissions_select") == '2':
                user.groups.add(driver_group, operator_group)
            if request.POST.get("permissions_select") == '3':
                user.groups.add(driver_group)

            user_form = CustomUserChangeForm(request.POST, instance=request.user)
            if "user" in next_url:
                next_url = "/user?success=0&tab=info"
            if "custom_admin" in next_url:
                next_url = "/custom_admin/?selected=" + str(user.username) + "&success=0"

            if user_form.is_valid():
                if "user" in next_url:
                    next_url = "/user?success=1&tab=info"
                if "custom_admin" in next_url:
                    next_url = "/custom_admin/?selected=" + str(user.username) + "&success=1"

                user.email = user_form.cleaned_data.get('email')
                user.first_name = user_form.cleaned_data.get('first_name')
                user.last_name = user_form.cleaned_data.get('last_name')
                user.address = user_form.cleaned_data.get('address')
                user.phone = user_form.cleaned_data.get('phone')
                user.save()

            return redirect(to=next_url)

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

def filter_offers(facility, request):
    is_filter = False
    if request.get('submit'):
        if request['submit'] == 'remove_filter':
            is_filter = False
        elif request['submit'] == 'search':
            is_filter = True

    filter_form = {
        'search': request.get('search', ''),
        'type': request.get('filter_type', ''),
        'daily': request.get('daily', None),
        'perm': request.get('perm', None)
    }

    search_field = filter_form['search']
    type_field = filter_form['type']

    offers = None
    if is_filter:
        if filter_form['daily'] is not None and filter_form['perm'] is not None:
            offers = Offer.objects.all()
        elif filter_form['daily'] is not None:
            offers = Offer.objects.filter(variant='D')
        elif filter_form['perm'] is not None:
            offers = Offer.objects.filter(variant='P')
    else:
        offers = Offer.objects.all()
        filter_form['daily'] = '1'
        filter_form['perm'] = '1'

    filtered_offers = {}
    if offers is not None:
        for offer in offers.order_by('variant'):
            if search_field != '':
                if type_field == 'type':
                    filtered_items = offer.items.filter(variant__contains=search_field)
                else:
                    filtered_items = offer.items.filter(name__contains=search_field)
            else:
                filtered_items = offer.items.all()
            filtered_offers[offer.pk] = {'items': filtered_items, 'name': offer.name, 'variant': offer.variant}
    return (filtered_offers, filter_form)

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

        filtered_offers, filter_form = filter_offers(facility, request.GET)

        is_open = is_fac_open(facility)
        context = {
            'facility': facility,
            'offers': filtered_offers,
            'can_order': True,
            'summary': {},
            'search_form': filter_form 
        }

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

#------------------------------

def operator(request):

    #set default values
    type_tab = None

    # <<<facility>>>
    facility_form = FacilityChangeForm()
    selected_facility = None
    facility_deleted = '-1'
    facility_changed = '-1'
    new_facility = '-1'

    # <<<offer>>>
    offer_form = OfferChangeForm()
    selected_offer = None
    offer_deleted = '-1'
    offer_changed = '-1'
    new_offer = '-1'

    # <<<food>>>
    food_form = FoodChangeForm()
    selected_food = None
    food_deleted = '-1'
    food_changed = '-1'
    new_food = '-1'

    # <<<drink>>>
    drink_form = DrinkChangeForm()
    selected_drink = None
    drink_deleted = '-1'
    drink_changed = '-1'
    new_drink = '-1'

    if request.method == 'GET':
        # <<<facility>>>
        id_facility = request.GET.get('selected_facility', '')
        facility_deleted = request.GET.get('facility_deleted', '')
        facility_changed = request.GET.get('facility_changed', '')
        new_facility = request.GET.get('new_facility', '')
        if id_facility != '':
            try:
                selected_facility = Facility.objects.get(pk=id_facility)
                facility_form = FacilityChangeForm(initial={ 'name' : selected_facility.name, 'address' : selected_facility.address, 'opening_time': selected_facility.opening_time,
                                                        'closing_time' : selected_facility.closing_time, 'state' : selected_facility.state,
                                                        'offers' : selected_facility.offers.all() })
            except Exception:
                ...

        # <<<offer>>>
        id_offer = request.GET.get('selected_offer', '')
        offer_deleted = request.GET.get('offer_deleted', '')
        offer_changed = request.GET.get('offer_changed', '')
        new_offer = request.GET.get('new_offer', '')
        if id_offer != '':
            try:
                selected_offer = Offer.objects.get(pk=id_offer)
                offer_form = OfferChangeForm(initial={ 'name' : selected_offer.name, 'variant' : selected_offer.variant,
                                                        'items' : selected_offer.items.all() })
            except Exception:
                ...

        # <<<food>>>
        id_food = request.GET.get('selected_food', '')
        food_deleted = request.GET.get('food_deleted', '')
        food_changed = request.GET.get('food_changed', '')
        new_food = request.GET.get('new_food', '')
        if id_food != '':
            try:
                selected_food = Food.objects.get(pk=id_food)
                food_form = FoodChangeForm(initial={ 'name' : selected_food.name, 'variant' : selected_food.variant,
                                    'img' : selected_food.img, 'price' : selected_food.price, 'in_stock' : selected_food.in_stock,
                                    'weight' : selected_food.weight, 'ingredients' : selected_food.ingredients})
            except Exception:
                ...

        # <<<drink>>>
        id_drink = request.GET.get('selected_drink', '')
        drink_deleted = request.GET.get('drink_deleted', '')
        drink_changed = request.GET.get('drink_changed', '')
        new_drink = request.GET.get('new_drink', '')
        if id_drink != '':
            try:
                selected_drink = Drink.objects.get(pk=id_drink)
                drink_form = DrinkChangeForm(initial={ 'name' : selected_drink.name, 'variant' : selected_drink.variant,
                                    'imt' : selected_drink.img, 'price' : selected_drink.price, 
                                    'in_stock' : selected_drink.in_stock, 'volume' : selected_drink.volume})
            except Exception:
                ...

        type_tab = request.GET.get('type', '')

    if request.method == 'POST':
        type_tab = request.POST.get('type') 
        if type_tab == 'facility':
            facility_form = FacilityChangeForm(request.POST, instance=request.user)
        elif type_tab == 'offer':
            offer_form = OfferChangeForm(request.POST, instance=request.user)
        elif type_tab == 'food':
            food_form = FoodChangeForm(request.POST, instance=request.user)
        elif type_tab == 'drink':
            drink_form = DrinkChangeForm(request.POST, instance=request.user)

    #send data
    context = { 'user' : request.user,
                'type' : type_tab,

                # <<<facility>>>
                'facilities' : Facility.objects.all(),
                'selected_facility' : selected_facility,
                'facility_deleted' : facility_deleted,
                'facility_changed' : facility_changed,
                'new_facility' : new_facility, 
                'fac_form' : facility_form,

                # <<<offer>>>
                'offers' : Offer.objects.all(),
                'selected_offer' : selected_offer,
                'offer_deleted' : offer_deleted,
                'offer_changed' : offer_changed,
                'new_offer' : new_offer,
                'offer_form' : offer_form,

                # <<<food>>>
                'foods' : Food.objects.all(),
                'selected_food' : selected_food,
                'food_deleted' : food_deleted,
                'food_changed' : food_changed,
                'new_food' : new_food,
                'food_form' : food_form,

                # <<<drink>>>
                'drinks' : Drink.objects.all(),
                'selected_drink' : selected_drink,
                'drink_deleted' : drink_deleted,
                'drink_changed' : drink_changed,
                'new_drink' : new_drink,
                'drink_form' : drink_form,
                }
    return render(request, 'app/operator.html', context)

def create_facility(request):
    code = '1'
    if request.method == 'POST':
        next_url = request.POST.get('next_url', '/')
        new_name = request.POST.get('new_facility_name')
        new_address = request.POST.get('new_facility_address')

        new_facility = Facility(name=new_name, address=new_address, opening_time=timezone.now(), closing_time=timezone.now(), state='D')        
        try:
            new_facility.save()
            code = '0'
        except Exception:
            code = '2'

    return redirect(to = next_url + '?new_facility=' + code)

def edit_facility(request):
    next_url = request.POST.get('next_url')
    name = request.POST.get('name')

    facility = None
    code = '2'
    if name != None:
        try:
            facility = Facility.objects.get(pk=name)
        except Exception:
            ...

    if facility != None:
        if request.method == 'POST':
            facility_form = FacilityChangeForm(request.POST, instance = request.user)

            if facility_form.is_valid():
                code = '0'

                facility.address = facility_form.cleaned_data.get('address')
                facility.opening_time = facility_form.cleaned_data.get('opening_time')
                facility.closing_time = facility_form.cleaned_data.get('closing_time')
                facility.state = facility_form.cleaned_data.get('state')
                facility.offers.set(facility_form.cleaned_data.get('offers'))
                facility.save()
            else:
                code = '1'
        
            # do not add '&facility_changed' if it is already in url
            s = '&facility_changed'
            if s in next_url:
                next_url = next_url.split(s)[0]

            return redirect(to = next_url + '&facility_changed=' + code)

    return redirect(to = next_url + '?facility_changed=' + code)

def delete_facility(request):
    next_url = request.POST.get('next_url')
    name = request.POST.get('name', '')

    code = '1'
    if name != '':
        try:
            print(Facility.objects.all())
            facility_to_delete = Facility.objects.get(pk=name)
            facility_to_delete.delete()
            code = '0'
        except Exception:
            ...

    return redirect(to = next_url + '?facility_deleted=' + code)

def create_offer(request):
    code = '1'
    if request.method == 'POST':
        type_tab = request.POST.get('type', '')
        next_url = request.POST.get('next_url', '/')
        new_name = request.POST.get('new_offer_name')
        new_variant = request.POST.get('new_variant')

        new_offer = Offer(name=new_name, variant=new_variant)        
        try:
            new_offer.save()
            code = '0'
        except Exception:
            code = '2'

    return redirect(to = next_url + '?new_offer=' + code + '&type=' + type_tab)

def edit_offer(request):
    next_url = request.POST.get('next_url')
    name = request.POST.get('name')

    offer = None
    code = '2'
    if name != None:
        try:
            offer = Offer.objects.get(pk=name)
        except Exception:
            ...

    if offer != None:
        if request.method == 'POST':
            offer_form = OfferChangeForm(request.POST, instance = request.user)

            if offer_form.is_valid():
                code = '0'

                offer.variant = offer_form.cleaned_data.get('variant')
                offer.items.set(offer_form.cleaned_data.get('items'))
                offer.save()
            else:
                code = '1'
        
            # do not add '&offer_changed' if it is already in url
            s = '&offer_changed'
            if s in next_url:
                next_url = next_url.split(s)[0]

            return redirect(to = next_url + '&offer_changed=' + code)

    if '?' in next_url:
        next_url = next_url.split('?')[0]
    return redirect(to = next_url + '?offer_changed=' + code + '&type=offer')

def delete_offer(request):
    type = request.POST.get('type', '')
    next_url = request.POST.get('next_url')
    name = request.POST.get('name', '')

    code = '1'
    if name != '':
        try:
            offer_to_delete = Offer.objects.get(pk=name)
            offer_to_delete.delete()
            code = '0'
        except Exception:
            ...

    return redirect(to = next_url + '?offer_deleted=' + code + '&type=' + type_tab)

def create_food(request):
    code = '1'
    if request.method == 'POST':
        type_tab = request.POST.get('type', '')
        next_url = request.POST.get('next_url', '/')
        new_name = request.POST.get('new_food_name')
        new_price = request.POST.get('new_food_price')
        new_weight = request.POST.get('new_food_weight')
        new_ingredients = request.POST.get('new_food_ingredients')

        new_food= Food(name=new_name, price=new_price, weight=new_weight, ingredients=new_ingredients, in_stock=False)        
        try:
            new_food.save()
            code = '0'
        except Exception:
            code = '2'

    return redirect(to = next_url + '?new_food=' + code + '&type=' + type_tab)

def edit_food(request):
    next_url = request.POST.get('next_url')
    name = request.POST.get('name')

    food = None
    code = '2'
    if name != None:
        try:
            food = Food.objects.get(pk=name)
        except Exception:
            ...

    if food != None:
        if request.method == 'POST':
            food_form = FoodChangeForm(request.POST, instance = request.user)

            if food_form.is_valid():
                code = '0'

                food.variant = food_form.cleaned_data.get('variant')
                food.img = food_form.cleaned_data.get('img')
                food.price = food_form.cleaned_data.get('price')
                food.in_stock = food_form.cleaned_data.get('in_stock')
                food.weight = food_form.cleaned_data.get('weight')
                food.ingredients = food_form.cleaned_data.get('ingredients')
                food.save()
            else:
                code = '1'
        
            # do not add '&food_changed' if it is already in url
            s = '&food_changed'
            if s in next_url:
                next_url = next_url.split(s)[0]

            return redirect(to = next_url + '&food_changed=' + code)

    if '?' in next_url:
        next_url = next_url.split('?')[0]
    return redirect(to = next_url + '?food_changed=' + code + '&type=food')

def delete_food(request):
    type_tab = request.POST.get('type', '')
    next_url = request.POST.get('next_url')
    name = request.POST.get('name', '')

    code = '1'
    if name != '':
        try:
            offer_to_delete = Food.objects.get(pk=name)
            offer_to_delete.delete()
            code = '0'
        except Exception:
            ...

    return redirect(to = next_url + '?food_deleted=' + code + '&type=' + type_tab)

def create_drink(request):
    code = '1'
    if request.method == 'POST':
        type_tab = request.POST.get('type', '')
        next_url = request.POST.get('next_url', '/')
        new_name = request.POST.get('new_drink_name')
        new_price = request.POST.get('new_drink_price')
        new_volume = request.POST.get('new_drink_volume')

        new_drink = Drink(name=new_name, price=new_price, volume=new_volume, in_stock=False)        
        try:
            new_drink.save()
            code = '0'
        except Exception:
            code = '2'

    return redirect(to = next_url + '?new_drink=' + code + '&type=' + type_tab)

def edit_drink(request):
    next_url = request.POST.get('next_url')
    name = request.POST.get('name')

    drink = None
    code = '2'
    if name != None:
        try:
            drink = Drink.objects.get(pk=name)
        except Exception:
            ...

    if drink != None:
        if request.method == 'POST':
            drink_form = DrinkChangeForm(request.POST, instance = request.user)

            if drink_form.is_valid():
                code = '0'

                drink.variant = drink_form.cleaned_data.get('variant')
                drink.img = drink_form.cleaned_data.get('img')
                drink.price = drink_form.cleaned_data.get('price')
                drink.in_stock = drink_form.cleaned_data.get('in_stock')
                drink.volume = drink_form.cleaned_data.get('volume')
                drink.save()
            else:
                code = '1'
        
            # do not add '&drink_changed' if it is already in url
            s = '&drink_changed'
            if s in next_url:
                next_url = next_url.split(s)[0]

            return redirect(to = next_url + '&drink_changed=' + code)

    if '?' in next_url:
        next_url = next_url.split('?')[0]
    return redirect(to = next_url + '?drink_changed=' + code + '&type=drink')

def delete_drink(request):
    type_tab = request.POST.get('type', '')
    next_url = request.POST.get('next_url')
    name = request.POST.get('name', '')

    code = '1'
    if name != '':
        try:
            offer_to_delete = Drink.objects.get(pk=name)
            offer_to_delete.delete()
            code = '0'
        except Exception:
            ...

    return redirect(to = next_url + '?drink_deleted=' + code + '&type=' + type_tab)

#------------------------------

def driver(request):
    context = { 'orders' : Order.objects.filter(handled_by=request.user.id).order_by('-date')[::-1],
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
    users = CustomUser.objects.all()
    selected_user = None
    user_form = CustomUserChangeForm()
    user_deleted = "-1"
    set_password = "-1"
    set_info = "-1"
    new_user = "-1"
    highest_group = None
        
    driver_group = Group.objects.get(name='Driver')
    operator_group = Group.objects.get(name='Operator')
    admin_group = Group.objects.get(name='Administrator')

    if request.method == 'GET':
        username = request.GET.get("selected",'')
        user_deleted = request.GET.get("user_deleted",'')
        set_password = request.GET.get("set_pass",'')
        set_info = request.GET.get("success",'')
        new_user = request.GET.get("new_user",'')

        if username != "":
            selected_user = CustomUser.objects.get(username = username)
            user_form = CustomUserChangeForm(initial={ 'username' : selected_user.username, 'email' : selected_user.email, 'first_name' : selected_user.first_name, 'last_name' : selected_user.last_name, 'address' : selected_user.address, 'phone' : selected_user.phone})
            if selected_user != None:
                if driver_group in selected_user.groups.all():
                    highest_group = "Driver"
                if operator_group in selected_user.groups.all():
                    highest_group = "Operator"
                if admin_group in selected_user.groups.all():
                    highest_group = "Administrator"

    else:
        user_form = CustomUserChangeForm(request.POST, instance=request.user)

    return render(request, 'app/admin.html', { 'users': users, 'selected_user' : selected_user, 'user_form' : user_form, 'user_deleted' : user_deleted, 'set_password' : set_password, 'set_info' : set_info, 'new_user' : new_user, 'highest_group' : highest_group })

def admin_set_user_password(request):
    next_url = request.POST.get('next_url')
    username = request.POST.get('username')

    if username == '':
        return redirect(to=next_url)

    if request.method == 'POST':
        new_password = request.POST.get('new_user_password')
        user = CustomUser.objects.get(username = username)
        if user != None:
            user.set_password(new_password)
            user.save()
            return redirect(to=next_url + "&set_pass=1")
    return redirect(to=next_url + "&set_pass=0")

def admin_create_user(request):
    if request.method == 'POST':
        next_url = request.POST.get('next_url','/')
        new_password = request.POST.get('new_user_password')
        new_username = request.POST.get('new_user')

        new_user = CustomUser(username = new_username)
        new_user.set_password(new_password)
        try:
            new_user.save()
            return(redirect(to = next_url + "?new_user=1"))
        except Exception:
            return(redirect(to = next_url + "?new_user=2"))
    return(redirect(to = next_url + "?new_user=0"))

def delete_user(request):
    next_url = request.POST.get('next_url')
    username = request.POST.get('username')

    if username != None and username != "":
        user_to_delete = CustomUser.objects.get(username = username)
        if user_to_delete != request.user:
            user_to_delete.delete()
            return redirect(to=next_url + "?user_deleted=1")
        else:
            return redirect(to=next_url + "?user_deleted=2")
            #TODO: jde smazat sám sebe?
    return redirect(to=next_url + "?user_deleted=0")

def register(request):

    next_url = request.GET.get('next', '/')
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
                return redirect(to = next_url)
            
            except Exception:
                user_exists = True           
    else:
        form = CustomUserCreationForm()

    return render(request, 'authentication/register.html', {'form': form, 'user_exists': user_exists})

def login_user(request):
    next_url = request.GET.get('next', '/')
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username = username, password = password)
            if user is not None:
                login(request, user)
                return redirect(to = next_url)
    else:
        form = CustomAuthenticationForm()

    return render(request, 'authentication/login.html', {'form': form})

def logout_user(request):
    logout(request)
    return render(request, 'authentication/logged_out.html')
