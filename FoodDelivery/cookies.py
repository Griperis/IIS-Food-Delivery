import json
from .models import Item
import datetime

def parse_order_state(item_count):
    ret_val = []
    total_price = 0
    for item_id, count in item_count.items():
        try:
            item = Item.objects.get(pk=item_id)
        except Item.DoesNotExist:
            continue
        total_price += item.price * count
        ret_val.append({'item': item, 'count': count})
    return {'order': ret_val, 'price': total_price}

def add_order_item(request, item_id, facility_id):
    order_state = request.COOKIES.get('order_state')
    if order_state is None:
        init_value = {facility_id: {}}
        init_value[facility_id][item_id] = 1
        return parse_order_state(init_value[facility_id])
    else:
        loaded_state = json.loads(order_state)
        if facility_id in loaded_state:
            if item_id in loaded_state[facility_id]:
                loaded_state[facility_id][item_id] += 1
            else:
                loaded_state[facility_id][item_id] = 1
            return parse_order_state(loaded_state[facility_id])
        else:
            return {'order': {}, 'prize': 0}

def remove_order_item(request, item_id, facility_id):
    order_state = request.COOKIES.get('order_state')
    if order_state is None:
        return {'order': {}, 'prize': 0}
    else:
        loaded_state = json.loads(order_state)
        if facility_id in loaded_state and item_id in loaded_state[facility_id]:
            loaded_state[facility_id][item_id] -= 1
            if loaded_state[facility_id][item_id] == 0:
                del loaded_state[facility_id][item_id]
        
        return parse_order_state(loaded_state[facility_id])

def load_order_state(request, facility_id):
    order_state = request.COOKIES.get('order_state')
    if order_state is None:
        return {'order': {}, 'prize': 0}
    else:
        item_count = json.loads(order_state)
        if facility_id in item_count:
            return parse_order_state(item_count[facility_id])
        else:
            return {'order': {}, 'prize':0}

def save_order_state(response, order_state, facility_id):
    to_serialize = {facility_id: {}}
    for entry in order_state:
        to_serialize[facility_id][str(entry['item'].pk)] = entry['count']
    response.set_cookie('order_state', json.dumps(to_serialize), max_age=300)

def remove_order_cookies(response):
    response.delete_cookie('order_state')

def save_form_state(response, form_state):
    response.set_cookie('form_state', json.dumps(form_state), max_age=300)

def remove_form_state(response):
    response.delete_cookie('form_state')

def load_form_state(request):
    form_state = request.COOKIES.get('form_state')
    if form_state is None:
        return {'type': '', 'search': ''}
    else:
        form_state = json.loads(form_state)
        print(form_state)
        return form_state


