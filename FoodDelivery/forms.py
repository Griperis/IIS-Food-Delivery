from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from .models import CustomUser, Food, Facility

from django.utils.translation import gettext_lazy as _

class CustomUserCreationForm(UserCreationForm):
    error_messages = {
        'password_mismatch': _("Hesla nejsou stejná."),
    }
    password1 = forms.CharField(
        label=_("Heslo"),
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text="TODO",
    )
    password2 = forms.CharField(
        label=_("Potvrzení Hesla"),
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        strip=False,
        help_text=_("Vložte znovu heslo"),
    )
    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'address', 'phone')
        labels = {'username': _('Uživatelské jméno'), 'email': _('Emailová adresa'),'first_name': _('Jméno'),
        'last_name': _('Příjmení'),'address': _('Adresa'),'phone': _('Telefonní číslo'),}
        widgets = {'username': forms.TextInput(attrs={'class': 'form-control'}),
                   'email': forms.TextInput(attrs={'class': 'form-control'}),
                   'first_name': forms.TextInput(attrs={'class': 'form-control'}),
                   'last_name': forms.TextInput(attrs={'class': 'form-control'}),
                   'address': forms.TextInput(attrs={'class': 'form-control'}),
                   'phone': forms.TextInput(attrs={'class': 'form-control'}),}

class CustomUserChangeForm(UserChangeForm):
    password = None
    
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
        label=_("Staré heslo"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autofocus': True, 'class': 'form-control'}),
    )
    new_password1 = forms.CharField(
        label=_("Nové heslo"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autofocus': True, 'class': 'form-control'}),
    )
    new_password2 = forms.CharField(
        label=_("Znovu nové heslo"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autofocus': True, 'class': 'form-control'}),
    )