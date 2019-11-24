python manage.py makemigrations FoodDelivery;
python manage.py migrate FoodDelivery;
python manage.py makemigrations;
python manage.py migrate;
echo "
from FoodDelivery.models import CustomUser, Facility, Offer, Order, Item, Food, Drink, OrderItem
from django.utils import timezone
from django.contrib.auth.models import Group
user = CustomUser.objects.create_superuser('iis-admin', 'admin@example.com', 'iis-fd-pass')
user.is_superuser=True
user.is_staff=True
user.save()

driver_g = Group(name='Driver')
driver_g.save()
operators_g = Group(name='Operator')
operators_g.save()
admin_g = Group(name='Administrator')
admin_g.save()
user.groups.add(driver_g, operators_g, admin_g)

facility_1 = Facility(name='Na purkynce', address='Ono 98 Tamto 765 15', state='A', opening_time=timezone.now(), closing_time=timezone.now(), min_prize=0)
facility_1.save()

beer = Drink(name='Pivo 12', variant='', in_stock=True, price=25, volume=500)
beer.save()

fries = Food(name='Smazene hranolky', in_stock=True, variant='', price=45, weight=200, ingredients='Brambory, sul')
fries.save()

drink_offer = Offer(name='Napoje', variant='P')
drink_offer.save()
drink_offer.items.add(beer)

food_offer = Offer(name='Prilohy', variant='P')
food_offer.save()
food_offer.items.add(fries)

facility_1.offers.add(food_offer, drink_offer)
" | python manage.py shell
