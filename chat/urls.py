from django.conf.urls import url

from . import views
app_name = 'chat'


urlpatterns = [
    url(r'^chat/$', views.Talk, name='chat'),

    url(r'^post/$', views.Post, name='post'),
    url(r'^messages/$', views.Messages, name='messages'),
]