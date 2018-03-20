from django.conf.urls import url
from django.contrib.auth import views as auth_views

from bbil import views as core_views


urlpatterns = [
    url(r'^login/$', auth_views.login, {'template_name': 'tippspiel/overview.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, {'template_name': 'tippspiel/overview.html', 'next_page': 'tippspiel_match_list'}, name='logout'),
    url(r'^signup/$', core_views.signup, name='signup'),
    url(r'^account_activation_sent/$', core_views.account_activation_sent, name='account_activation_sent'),
    url(r'^accounts/profile/$', core_views.profile, name='profile'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        core_views.activate, name='activate'),
]
