from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, Facility, Offer, Order, Item, Food, Drink

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['email', 'username', 'phone']
    fieldsets = ( (None, {'fields': ('address','phone')}), ) + UserAdmin.fieldsets

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Facility)
admin.site.register(Offer)
admin.site.register(Order)
admin.site.register(Food)
admin.site.register(Drink)
