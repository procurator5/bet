from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.db.models import Sum, Count

from bbil.forms import SignUpForm, BitcoinEscrow
from bbil.tokens import account_activation_token
from bbil.models import Profile

from tippspiel.models import Tipp

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

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
    bet_count = Tipp.objects.filter(player=request.user, state = "In Game").all().aggregate(Count('amount'))['amount__count'] 
    print(bet_count)
    return render(
        request,
        'bbil/profile.html',
        {
            'wallet': profile.wallet,
            'betCount': bet_count,
            'inGame': 0 if bet_count == 0 else Tipp.objects.filter(player=request.user, state = "In Game").all().aggregate(Sum('amount'))['amount__sum'],
        },
    )
    
@login_required
def pay(request):
    profile =Profile.objects.get(user=request.user)
    recv_address = profile.wallet.receiving_address(fresh_addr=False)

    try:
        amount = float(request.POST.get("amount"))
    except TypeError:
        amount = 0.1

    return render(
        request,
        'bbil/pay.html',
        {
            'wallet': profile.wallet,
            'amount': amount,
        },
    )
    
@login_required
def escrow(request):

    if request.method == 'POST':
        form = BitcoinEscrow(request.POST)
        if form.is_valid():
            profile =Profile.objects.get(user=request.user)
            #WalletTransaction
            bwt = profile.wallet.send_to_address(form.cleaned_data['bitcoin_address'], form.cleaned_data['amount'])
            print(bwt)
    else:
        form = BitcoinEscrow()
    return render(
        request,
        'bbil/escrow.html',
        {
            'form': form
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
    

@login_required
def settings(request):
    errors = []
    return render(
        request,
        'bbil/settings.html',
        {
            'errors': errors
        },
    )
