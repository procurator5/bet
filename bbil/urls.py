from django.conf.urls import url
from django.contrib.auth import views as auth_views

from bbil import views as core_views


urlpatterns = [
    url(r'^login/$', auth_views.login, {'template_name': 'tippspiel/overview.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, {'template_name': 'tippspiel/overview.html', 'next_page': 'tippspiel_match_list'}, name='logout'),
    #registration
    url(r'^signup/$', core_views.signup, name='signup'),
    url(r'^account_activation_sent/$', core_views.account_activation_sent, name='account_activation_sent'),
    url(r'^accounts/profile/$', core_views.profile, name='profile'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        core_views.activate, name='activate'),
    #password reset             
    url(r'^password_reset/$', auth_views.password_reset, name='password_reset'),
    url(r'^password_reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm, name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.password_reset_complete, name='password_reset_complete'),
    #password change
    url(r'^change-password/$', auth_views.password_change, name="password_change"),
    url(r'^password-change-done/$', auth_views.password_change_done,
    name='password_change_done'),
                                  
    url(r'^pay/$', core_views.pay, name='pay'),
    url(r'^escrow/$', core_views.escrow, name='escrow'),
    url(r'^history/$', core_views.history, name='history'),
    url(r'^outgoing/$', core_views.outgoing, name='outgoing'),
    url(r'^deposit/$', core_views.deposit, name='deposit'),
    url(r'^betsHistory/$', core_views.bets, name='bets'),
    url(r'^settings/$', core_views.settings, name='settings'),

]
