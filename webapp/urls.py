"""webapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from trelloBoard.views import GetApiToken
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token 

app_name = 'webapp'

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', GetApiToken.as_view()),
    url(r'^', include('login.urls')),
    url(r'^', include('chat.urls')),
    url(r'^', include('trelloBoard.urls')),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth')

]

if settings.DEBUG:
    import debug_toolbar
    from django.urls import include
    urlpatterns += path('__debug__/', include(debug_toolbar.urls)),
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
