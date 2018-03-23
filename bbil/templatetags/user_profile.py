from django import template
from bbil.models import Profile

register = template.Library()

@register.simple_tag(takes_context=True)
def user_balance(context):
    request = context['request']
    prof = Profile.objects.get(user = request.user)
    return prof.wallet.total_balance()
    