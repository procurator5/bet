from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string

from bbil.forms import SignUpForm
from bbil.tokens import account_activation_token
from bbil.models import Profile

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            print(urlsafe_base64_encode(force_bytes(user.pk)))
            current_site = get_current_site(request)
            subject = 'Activate Your MySite Account'
            message = render_to_string('bbil/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': force_text(urlsafe_base64_encode(force_bytes(user.pk))),
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject, message)

            return redirect('account_activation_sent')
    else:
        form = SignUpForm()
    return render(request, 'bbil/signup.html', {'form': form})


def account_activation_sent(request):
    return render(request, 'bbil/account_activation_sent.html')


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.profile.email_confirmed = True
        user.save()
        login(request, user)
        return redirect('/')
    else:
        return render(request, 'bbil/account_activation_invalid.html')

@login_required    
def profile(request):
    profile =Profile.objects.get(user=request.user)
    recv_address = profile.wallet.receiving_address(fresh_addr=False)
    return render(
        request,
        'bbil/profile.html',
        {
            'bitcoin_account': recv_address
        },
    )
    
@login_required
def pay(request):
    return render(
        request,
        'bbil/pay.html',
        {
        },
    )
    
@login_required
def bitcoin(request):
    return render(
        request,
        'bbil/bitcoin.html',
        {
        },
    )
    
