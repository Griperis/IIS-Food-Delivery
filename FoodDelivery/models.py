from django.contrib.auth.models import AbstractUser
from django.db import models

class Item(models.Model):
    name = models.CharField(max_length=100)
    variant = models.CharField(max_length=200, blank=True)
    img = models.ImageField(null=True, blank=True)
    price = models.IntegerField()
    in_stock = models.BooleanField()

    def __str__(self):
        return self.name


class Drink(Item):
    volume = models.IntegerField()


class Food(Item):
    weight = models.IntegerField()
    ingredients = models.CharField(max_length=300)


class CustomUser(AbstractUser):
    phone = models.CharField(max_length=50, null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)

    def get_phone(self):
        return self.phone

    def get_address(self):
        return self.address

class Order(models.Model):
    ORDER_STATE = (
        ('A', 'ACCEPTED'),
        ('D', 'DELIVERING'),
        ('F', 'FINISHED')
    )
    items = models.ManyToManyField(to=Item, through='OrderItem', through_fields=('order', 'item'))
    state = models.CharField(max_length=100, choices=ORDER_STATE, default=ORDER_STATE[0])
    date = models.DateTimeField(auto_now=True, editable=False)
    price = models.IntegerField()
    belongs_to = models.ForeignKey(to='FoodDelivery.Facility', on_delete=models.CASCADE)
    created_by = models.ForeignKey(CustomUser, related_name='CreatedBy', on_delete=models.SET_NULL, null=True, blank=True)
    handled_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return "Order: " + str(self.pk)

class OrderItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    count = models.IntegerField()

    def __str__(self):
        return "Order: " + str(self.item) + " " + str(self.order)

class Offer(models.Model):
    OFFER_VARIANT = (
        ('D', 'DAILY_OFFER'),
        ('P', 'PERMANENT_OFFER')
    )
    name = models.CharField(max_length=100, default='Default offer name')
    variant = models.CharField(max_length=20, choices=OFFER_VARIANT) 
    items = models.ManyToManyField(Item, blank=True)
    
    def __str__(self):
        return 'pk: ' + str(self.pk) + ' variant: ' + str(self.variant)


class Facility(models.Model):
    FACILITY_STATE = (
        ('A', 'ACCEPTS_ORDERS'),
        ('D', 'DNA_ORDERS'),
    )

    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    opening_time = models.TimeField(name='opening_time')
    closing_time = models.TimeField(name='closing_time')
    state = models.CharField(max_length=20, choices=FACILITY_STATE)
    offers = models.ManyToManyField(to=Offer, blank=True)
    min_price = models.IntegerField(default=0)

    
    def __str__(self):
        return self.name
