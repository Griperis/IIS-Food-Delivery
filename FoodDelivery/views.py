from django.shortcuts import render

def index(request):
    return render(request, 'FoodDelivery/index.html')