from django.shortcuts import render, redirect, get_object_or_404, HttpResponse, loader, HttpResponseRedirect
from .models import CustomUser, Facility, Offer, Order, Item, Food, Drink, OrderItem
from .forms import CustomUserCreationForm
import datetime
from .cookies import *

def index(request):

    facilities = Facility.objects.all()

    return render(request, 'app/index.html', {'facilities': facilities})

def user_profile(request):
    user = request.user
    orders = Order.objects.all().filter(created_by = user)
    success = False


    if request.method == 'GET':
        success = "true" == request.GET.get("success",'')

        user_form = CustomUserChangeForm(initial={ 'username' : user.username, 'email' : user.email, 'first_name' : user.first_name, 'last_name' : user.last_name, 'address' : user.address, 'phone' : user.phone})
        password_form = PasswordChangeForm(user = user)

    return render(request, 'app/user_profile.html', {'orders' : orders, 'user_form' : user_form, 'password_form' : password_form, 'success' : success})

def filter_offers(facility, search_field, type_field):
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

def facility_detail(request, facility_id):
    if request.method == 'POST':
        order_state = load_order_state(request, str(facility_id))
        create_new_order(order_state, facility_id, request.user)
        response = redirect('user_profile')
        remove_order_cookies(response)
        return response
    else:
        facility = get_object_or_404(Facility, pk=facility_id)

        search_field = ''
        type_field = ''
        if request.GET.get('search'):
            search_field = request.GET['search']
        if request.GET.get('filter-type'):
            type_field = request.GET['filter-type']

        search_form = {'search': search_field, 'type': type_field}
        filtered_offers = filter_offers(facility, search_field, type_field)

        now = datetime.datetime.now().time()
        is_open = now >= facility.opening_time and facility.closing_time <= now
        print(is_open)
        context = {'facility': facility, 'offers': filtered_offers, 'can_order': True, 'summary': {}, 'search_form': search_form }

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
        response = render(request, 'app/facility/facility_detail.html', context)

        if (order_summary):
            save_order_state(response, order_summary['order'], str(facility_id))
        return response

def order_summary(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    return render(request, 'app/order/order_summary.html', {'order': order })

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
