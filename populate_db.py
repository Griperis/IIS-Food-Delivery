
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "FoodDeliveryProject.settings")
django.setup()

from FoodDelivery.models import CustomUser, Facility, Offer, Order, Item, Food, Drink, OrderItem
from django.utils import timezone
from django.contrib.auth.models import Group
from django.core.files import File
from io import BytesIO
from urllib.request import urlopen 
import datetime


def get_remote_image(name):
    url = 'https://iis-fd.s3.eu-central-1.amazonaws.com/media/' + name + '.jpg'
    response = urlopen(url)
    io = BytesIO(response.read())
    file = File(io)

    return (name, file)

dj_admin = CustomUser.objects.create_superuser('iis-admin', 'admin@jidelny.cz', 'iis-fd-pass')
dj_admin.is_superuser=True
dj_admin.is_staff=True
dj_admin.save()

driver_g = Group(name='Driver')
driver_g.save()
operators_g = Group(name='Operator')
operators_g.save()
admin_g = Group(name='Administrator')
admin_g.save()
dj_admin.groups.add(driver_g, operators_g, admin_g)

operator = CustomUser.objects.create_user('operator', 'operator@jidelny.cz', 'operator', address='Slatinská 15, 604 72') 
operator.save()
operator.groups.add(operators_g)


ridic = CustomUser.objects.create_user('ridic', 'ridic@jidelny.cz', 'ridic', address='Purkyňova 72, 602 00')
ridic.save()
ridic.groups.add(driver_g)

franta = CustomUser.objects.create_user('franta', 'franta@seznam.cz', 'franta', address='Slovanské náměstí 28, 602 02')
franta.save()



veveri = Facility(name='Veveří', address='Veveří 493, 602 00', opening_time=datetime.time(10,30), closing_time=datetime.time(14, 00), state='A', min_price=80)
cejl = Facility(name='Jídelna Cejl', address='Hvězdová 289, 602 00', opening_time=datetime.time(8,00), closing_time=datetime.time(18, 00), state='A', min_price=0)
semilasso = Facility(name='Rychlé občerstvení Semilasso', address='Palackého tř. 124, 612 00', opening_time=datetime.time(16,30), closing_time=datetime.time(22, 00), state='A', min_price=150)

veveri.save()
cejl.save()
semilasso.save()
    


gulas = Food(name='Srnčí guláš', price=140, in_stock=True, weight=400, ingredients='Paprika, srnčí maso')
svickova = Food(name='Svíčková', price=120, in_stock=True, weight=350, ingredients='Smetana, hovězí svíčkové maso')
smazak = Food(name='Smažený sýr', price=90, in_stock=False, weight=150, ingredients='Gouda, strouhanka')
vkz = Food(name='Vepřo,knedlo, zelo', price=160, in_stock=True, weight=250, ingredients='Vepřové maso, zelí, knedlíky')

svickova.save()
smazak.save()
gulas.save()
vkz.save()

gulas.img.save(*get_remote_image('gulas'), save=True)
svickova.img.save(*get_remote_image('svickova'), save=True)
smazak.img.save(*get_remote_image('smazak'), save=True)
vkz.img.save(*get_remote_image('vkz'), save=True)


ceska_klasika = Offer(name='Česká klasika', variant='P')
ceska_klasika.save()
ceska_klasika.items.add(gulas, svickova, smazak, vkz)

hranolky = Food(name='Smažené hranolky', price=40, in_stock=True, weight=200, ingredients='Brambory, sůl')
brambory = Food(name='Vařené brambory', price=30, in_stock=True, weight=200, ingredients='Brambory', variant='Bez lepku')

hranolky.save()
brambory.save()

hranolky.img.save(*get_remote_image('hranolky'), save=True)
brambory.img.save(*get_remote_image('brambory'), save=True)

prilohy = Offer(name='Přílohy', variant='P')
prilohy.save()
prilohy.items.add(hranolky, brambory)

polRajska = Food(name='Rajská', price=25, in_stock=True, weight=150, ingredients='Rajčata, rýže', variant='Diabetické')
polKureci = Food(name='Kuřecí vývar', price=25, in_stock=True, weight=150, ingredients='Vývar, bezlepkové nudle', variant='Bez lepku')
polCesnekova = Food(name='Česneková', price=25, in_stock=True, weight=150, ingredients='Vývar, česnek, šunka, sýr')
polHoubova = Food(name='Houbová', price=25, in_stock=True, weight=150)

polRajska.save()
polKureci.save()
polCesnekova.save()
polHoubova.save()

polRajska.img.save(*get_remote_image('pol_raj'), save=True)
polKureci.img.save(*get_remote_image('pol_kur'), save=True)
polCesnekova.img.save(*get_remote_image('pol_ces'), save=True)
polHoubova.img.save(*get_remote_image('pol_hub'), save=True)


polevky = Offer(name='Polévky', variant='P')
polevky.save()

polevky.items.add(polRajska, polKureci, polCesnekova, polHoubova)

radegast10_velke = Drink(name='Radegast 10° - velké', price=30, in_stock=True, volume=500)
radegast10_male = Drink(name='Radegast 10° - malé', price=22, in_stock=True, volume=300)

plzen12_velke = Drink(name='Plzen 12° - velké', price=35, in_stock=True, volume=500)
plzen12_male = Drink(name='Plzen 12° - malé', price=25, in_stock=True, volume=300)

kofola_velka = Drink(name='Kofola - velká', price=35, in_stock=True, volume=500)
kofola_mala = Drink(name='Kofola - malá', price=22, in_stock=True, volume=300)

dzus_pom = Drink(name='Pomerančový džus', price=30, in_stock=True, volume=300)
dzus_jah = Drink(name='Jahodový džus', price=30, in_stock=False, volume=300)

radegast10_male.save()
radegast10_velke.save()
plzen12_male.save()
plzen12_velke.save()
kofola_mala.save()
kofola_velka.save()
dzus_jah.save()
dzus_pom.save()

radegast10_male.img.save(*get_remote_image('radegast'), save=True)
radegast10_velke.img.save(*get_remote_image('radegast'), save=True)
plzen12_male.img.save(*get_remote_image('plzen'), save=True)
plzen12_velke.img.save(*get_remote_image('plzen'), save=True)
kofola_mala.img.save(*get_remote_image('kofola'), save=True)
kofola_velka.img.save(*get_remote_image('kofola'), save=True)
dzus_jah.img.save(*get_remote_image('dzus_jah'), save=True)
dzus_pom.img.save(*get_remote_image('dzus_pom'), save=True)


alkohol = Offer(name='Pivo', variant='P')
alkohol.save()
alkohol.items.add(radegast10_velke, radegast10_male, plzen12_male, plzen12_velke)

nealko = Offer(name='Nealkoholické nápoje', variant='P')
nealko.save()
nealko.items.add(kofola_mala, kofola_velka, dzus_pom, dzus_jah)

denni = Offer(name='Denní nabídka', variant='D')
denni.save()
denni.items.add(polRajska, svickova, smazak)



veveri.offers.add(ceska_klasika, denni, alkohol, nealko)
cejl.offers.add(ceska_klasika, polevky, prilohy, alkohol, nealko)
semilasso.offers.add(polevky, alkohol, nealko)