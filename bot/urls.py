from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^(?P<token>[\w:-]+)$', views.bot_endpoint, name='bot_endpoint')
]
