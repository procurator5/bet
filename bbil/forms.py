from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django_bitcoin.BCAddressField import is_valid_btc_address


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2' )
        
        
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