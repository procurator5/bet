from django import template
from bbil.models import Profile
from django_bitcoin import  currency

register = template.Library()

@register.simple_tag(takes_context=True)
def user_balance(context):
    request = context['request']
    amount = request.user.profile.wallet.total_balance()
    if request.user.profile.currency != 'BTC':
        amount=currency.btc2currency(amount, request.user.profile.currency)    
    return str(amount) + " " + request.user.profile.currency
    