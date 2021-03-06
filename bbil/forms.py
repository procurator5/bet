from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django_bitcoin.BCAddressField import is_valid_btc_address
import pytz

currencies = (
    ("USD", "USD"),
    ("EUR", "EUR"),
    ("BTC", "BTC")
)

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.', label='E-mail:')
    timezone = forms.ChoiceField(choices=[(x, x) for x in pytz.common_timezones], label='Tour time zone:')
    currency = forms.ChoiceField(choices=currencies, label="Account's currency")
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2' )
        
class ChangeProfileForm(forms.Form):
    username = forms.CharField(max_length=64, label='Username:')
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.', label='E-mail:')
    timezone = forms.ChoiceField(choices=[(x, x) for x in pytz.common_timezones], label='Your time zone:')
    currency = forms.ChoiceField(choices=currencies, label="Account's currency")
    
    class Meta:
        model = User
        fields = ('username', 'email', )
        exclude = ('password1','password2',)
        

        
class BitcoinEscrow(forms.Form):
    bitcoin_address = forms.CharField()
    amount = forms.DecimalField(
        max_digits=16,
        decimal_places=8,        
        )
    
    def clean_bitcoin_address(self):
        addr = self.cleaned_data['bitcoin_address']
        if not is_valid_btc_address(addr):
            raise forms.ValidationError(("Not a valid bitcoin address: %(addr)s"),
                                        params={'addr': addr},
                                        )
        return addr
    
    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount < 0:
            raise forms.ValidationError(("Amount less than zero"),
                                        )
            
        
        return amount