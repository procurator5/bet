from django import template
from bbil.models import Profile

register = template.Library()

@register.simple_tag(takes_context=True)
def user_balance(context):
    request = context['request']
    return str(request.user.profile.wallet.total_balance()) + " " + request.user.profile.currency
    