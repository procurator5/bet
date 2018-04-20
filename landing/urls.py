from django.conf.urls import url
from landing.views import *

urlpatterns = [
    url(
        r'^$',
        index,
        name='landing'        
    ),
]