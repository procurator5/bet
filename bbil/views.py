from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.db.models import Sum, Count

from bbil.forms import SignUpForm, BitcoinEscrow, ChangeProfileForm
from bbil.tokens import account_activation_token
from bbil.models import Profile

from django_bitcoin import  currency

from tippspiel.models import Tipp
import decimal

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

            return redirect('tippspiel_match_list')
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
    return render(
        request,
        'bbil/profile.html',
        {
            'wallet': profile.wallet,
            'betCount': bet_count,
            'inGame': 0 if bet_count == 0 else Tipp.objects.filter(player=request.user, state = "In Game").all().aggregate(Sum('amount'))['amount__sum'],
            'to_outgoing': profile.to_outgoing()
        },
    )
    
@login_required
def pay(request):
    profile =Profile.objects.get(user=request.user)
    try:
        amount = decimal.Decimal(request.POST.get("amount"))
        amount = currency.currency2btc(amount, profile.currency)
    except decimal.InvalidOperation:
        amount = 0.001

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
            amount = currency.currency2btc(form.cleaned_data['amount'], profile.currency)
            bwt = profile.wallet.send_to_address(form.cleaned_data['bitcoin_address'], amount)
            return redirect('outgoing')            
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
def history(request):
    profile =Profile.objects.get(user=request.user)
    hisitems = profile.history()
    return render(
        request,
        'bbil/history.html',
        {
            'hisitems': hisitems,
            'all': True,
        },
    )

@login_required    
def outgoing(request):
    profile =Profile.objects.get(user=request.user)
    hisitems = profile.outgoing()
    return render(
        request,
        'bbil/history.html',
        {
            'hisitems': hisitems,
            'outgoing': True,
        },
    )
@login_required    
def bets(request):
    profile =Profile.objects.get(user=request.user)
    hisitems = profile.bets()
    return render(
        request,
        'bbil/history.html',
        {
            'hisitems': hisitems,
            'bets': True,
        },
    )


@login_required    
def deposit(request):
    profile =Profile.objects.get(user=request.user)
    hisitems = profile.deposit()
    return render(
        request,
        'bbil/history.html',
        {
            'hisitems': hisitems,
            'deposit': True,
        },
    )


@login_required
def settings(request):
    form = ChangeProfileForm(initial={'username': request.user.username, 
                                   'email': request.user.email, 
                                   #'password1': request.user.password1, 
                                   #'password2': request.user.password2,
                                   'timezone': request.user.profile.timezone,
                                   'currency': request.user.profile.currency,
                                   }
                          ) 
    form.fields['username'].widget.attrs['readonly'] = True

    if request.method == 'POST':
        form = ChangeProfileForm(request.POST)
        if form.is_valid():
            request.user.profile.timezone = form.cleaned_data['timezone']
            request.user.profile.currency = form.cleaned_data['currency']
            request.user.profile.save()
            request.user.email = form.cleaned_data['email']
            request.user.save()
    
    return render(
        request,
        'bbil/settings.html',
        {
            'form': form,
        },
    )
