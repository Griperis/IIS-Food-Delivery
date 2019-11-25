from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm, AuthenticationForm, UsernameField
from .models import CustomUser, Food, Facility
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
        labels = {'email': _('Emailová adresa'),'first_name': _('Jméno'),'last_name': _('Příjmení'),'address': _('Adresa'),'phone': _('Telefonní číslo'),}
        widgets = {'email': forms.TextInput(attrs={'class': 'form-control'}),
                   'first_name': forms.TextInput(attrs={'class': 'form-control'}),
                   'last_name': forms.TextInput(attrs={'class': 'form-control'}),
                   'address': forms.TextInput(attrs={'class': 'form-control'}),
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
        labels = {'email': _('Emailová adresa'),'first_name': _('Jméno'),'last_name': _('Příjmení'),'address': _('Adresa'),'phone': _('Telefonní číslo'),}
        widgets = {'email': forms.TextInput(attrs={'class': 'form-control'}),
                   'first_name': forms.TextInput(attrs={'class': 'form-control'}),
                   'last_name': forms.TextInput(attrs={'class': 'form-control'}),
                   'address': forms.TextInput(attrs={'class': 'form-control'}),
                   'phone': forms.TextInput(attrs={'class': 'form-control'}),}
                
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