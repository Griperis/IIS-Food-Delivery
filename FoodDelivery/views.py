from django.shortcuts import render
from .models import CustomUser, Facility, Offer, Order, Item, Food, Drink

def index(request):

    facilities = Facility.objects.all()

    return render(request, 'FoodDelivery/index.html', {"facilities":facilities})
