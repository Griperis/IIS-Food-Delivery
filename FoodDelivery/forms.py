from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm, AuthenticationForm, UsernameField
from .models import CustomUser, Food, Drink, Facility, Offer, Item
import re 

from django.utils.translation import gettext_lazy as _

def is_valid_phone(phone):
    if phone == None:
        return True
    if re.match(r"^(\+?)((\s)?\d{3}){3,4}$",phone) != None:
        return True
    return False

class CustomUserCreationForm(UserCreationForm):
    def clean_phone(self):
        cleaned_data = self.clean()
        phone = cleaned_data.get('phone')
        if not is_valid_phone(phone):
            self.add_error('phone', "Špatný formát telefonního čísla")
        return phone

    username = forms.CharField(label=_("Uživatelské jméno*"), strip=False, widget=forms.TextInput(attrs={'class': 'form-control'}),)

    password1 = forms.CharField(
        label=_("Heslo*"),
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    password2 = forms.CharField(
        label=_("Heslo znovu*"),
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        strip=False,
    )

    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'address', 'phone')
        labels = {'email': _('Emailová adresa'),'first_name': _('Jméno'),'last_name': _('Příjmení'),'address': _('Adresa*'),'phone': _('Telefonní číslo'),}
        widgets = {'email': forms.TextInput(attrs={'class': 'form-control'}),
                   'first_name': forms.TextInput(attrs={'class': 'form-control'}),
                   'last_name': forms.TextInput(attrs={'class': 'form-control'}),
                   'address': forms.TextInput(attrs={'class': 'form-control', 'required':'true'}),
                   'phone': forms.TextInput(attrs={'class': 'form-control'}),}

class CustomUserChangeForm(UserChangeForm):
    password = None
    
    def clean_phone(self):
        cleaned_data = self.clean()
        phone = cleaned_data.get('phone')
        if not is_valid_phone(phone):
            print("Spatny telefon")
            self.add_error('phone', "Špatný formát telefonního čísla")
        return phone

    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'address', 'phone')
        labels = {'email': _('Emailová adresa'),'first_name': _('Jméno'),'last_name': _('Příjmení'),'address': _('Adresa*'),'phone': _('Telefonní číslo'),}
        widgets = {'email': forms.TextInput(attrs={'class': 'form-control'}),
                   'first_name': forms.TextInput(attrs={'class': 'form-control'}),
                   'last_name': forms.TextInput(attrs={'class': 'form-control'}),
                   'address': forms.TextInput(attrs={'class': 'form-control', 'required' : 'true'}),
                   'phone': forms.TextInput(attrs={'class': 'form-control'}),}

class FacilityChangeForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(FacilityChangeForm, self).__init__(*args, **kwargs)

        if ('initial', 'offers') in kwargs:
            check_offers = [offer.pk for offer in kwargs['initial']['offers']]
            self.initial['offers'] = check_offers
    
    state = forms.ChoiceField(choices=[('A', 'Přijímá objednávky'), ('D', 'Nepřijímá objednávky')], label=_('Stav'))
    offers = forms.ModelMultipleChoiceField(queryset=Offer.objects.all(), required=False, label=_('Nabídky'), 
                                            widget=forms.CheckboxSelectMultiple(), )

    class Meta:
        model = Facility
        fields = ('name', 'address', 'opening_time', 'closing_time', 'state', 'offers')
        labels = {'name' : _('Jméno'), 'address' : _('Adresa'), 'opening_time' : _('Otevírací doba'), 
                    'closing_time' : _('Zavírací doba')}
        widgets = { 'name' : forms.TextInput(attrs={'class' : 'form-control'}),
                    'address' : forms.TextInput(attrs={'class' : 'form-control'}), 
                    'opening_time' : forms.TimeInput(attrs={'class': 'form-control'}),
                    'closing_time' :  forms.TimeInput(attrs={'class': 'form-control'}),   
                    }

class OfferChangeForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(OfferChangeForm, self).__init__(*args, **kwargs)

        print('kwargs: ', kwargs)
        if ('initial', 'items') in kwargs:
            check_items = [item.pk for item in kwargs['initial']['offers']]
            self.initial['items'] = check_items

    variant = forms.ChoiceField(choices=[('D', 'Denní nabídka'), ('P', 'Stála nabídka')], label=_('Stav'))
    items = forms.ModelMultipleChoiceField(queryset=Item.objects.all(), required=False, label=_('Pokrmy'), 
                                            widget=forms.CheckboxSelectMultiple(), )

    class Meta:
        model = Offer
        fields = ('name', 'variant', 'items')
        labels = {'name' : _('Název'), }
        widgets = { 'name' : forms.TextInput(attrs={'class' : 'form-control'}), }

class FoodChangeForm(forms.ModelForm):

    class Meta:
        model = Food
        fields = {'name', 'variant', 'img', 'price', 'in_stock', 'weight', 'ingredients'}
        labels = {'name' : _('Název'), 'variant' : _('Typ'), 'img' : _('Obrázek'), 'price' : _('Cena'), 
                    'in_stock' : _('Dostupnost'), 'weight' : _('Gramáž'), 'ingredients' : _('Složení')}
        widgets = {'name' : forms.TextInput(attrs={'class' : 'form-control'}),
                    'variant' : forms.TextInput(attrs={'class' : 'form-control'}),}

    field_order = ['name', 'variant', 'img', 'in_stock', 'price' , 'weight', 'ingredients']

class DrinkChangeForm(forms.ModelForm):

    class Meta:
        model = Drink
        fields = {'name', 'variant', 'img', 'price', 'in_stock', 'volume'}
        labels = {'name' : _('Název'), 'variant' : _('Typ'), 'img' : _('Obrázek'), 'price' : _('Cena'), 
                    'in_stock' : _('Dostupnost'), 'volume' : _('Objem (ml)'), }
        widgets = {'name' : forms.TextInput(attrs={'class' : 'form-control'}),
                    'variant' : forms.TextInput(attrs={'class' : 'form-control'}),}

    field_order = ['name', 'variant', 'img', 'in_stock', 'price' , 'volume']

class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label=_("Staré heslo*"),
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    new_password1 = forms.CharField(
        label=_("Nové heslo*"),
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    new_password2 = forms.CharField(
        label=_("Znovu nové heslo*"),
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )

class CustomAuthenticationForm(AuthenticationForm):
    username = UsernameField(label=_("Uživatelské jméno"),widget=forms.TextInput(attrs={'autofocus': True, 'class': 'form-control'}))
    password = forms.CharField(label=_("Heslo"),strip=False,widget=forms.PasswordInput(attrs={'class': 'form-control'}),)
    error_messages = {'invalid_login': _("Špatné uživatelské jméno nebo heslo."),'inactive': _("Tento účet je neaktivní."),}
    