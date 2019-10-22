from django.db import models

class Item(models.Model):
    name = models.CharField(max_length=100)
    variant = models.CharField(max_length=200)
    img = models.ImageField(null=True)
    prize = models.IntegerField()


class Drink(Item):
    volume = models.IntegerField()


class Food(Item):
    weight = models.IntegerField()
    ingredients = models.CharField(max_length=300)


class Order(models.Model):
    ORDER_STATE = (
        ('A', 'ACCEPTED'),
        ('D', 'DELIVERING'),
        ('F', 'FINISHED'),
    )
    items = models.ManyToManyField(to=Item)
    state = models.CharField(max_length=100, choices=ORDER_STATE)
    date = models.DateTimeField(auto_now=True)
    prize = models.IntegerField()
    belongs_to = models.ForeignKey(to='FoodDelivery.Facility', on_delete=models.CASCADE)





class Offer(models.Model):
    OFFER_VARIANT = (
        ('D', 'DAILY_OFFER'),
        ('P', 'PERMANENT_OFFER')
    )
    variant = models.CharField(max_length=20, choices=OFFER_VARIANT) 
    items = models.ManyToManyField(Item)
    
    def __str__(self):
        return 'pk: ' + self.pk + ' variant: ' + self.variant    


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
    offers = models.ManyToManyField(to=Offer)
    
    def __str__(self):
        return self.name
    

# User models (TODO)