from django.conf.urls import url
from django.urls import path, include
from . import views
from rest_framework import routers

app_name = 'login'
router = routers.DefaultRouter()

urlpatterns = [
    # /home/
    url(r'^home/$', views.ConnexionView.as_view(), name='connexion'),

    # /login/register/
    url(r'register/$', views.UserFormView.as_view(), name='register'),

    # /login/modif/
    # url(r'modif/$',views.ModifUsager.as_view(), name='usager-modifier'),

    # /login/user/user_id/
    url(r'^user-(?P<slug>[\w-]+)/$', views.ProfileView.as_view(), name='detail'),

    # /login/user/user_id/
    url(r'^user-(?P<slug>[\w-]+)/update/$', views.ModifUpdate.as_view(), name='user-update'),

    url(r'^add_fichier/$', views.CreationFile.as_view(), name='add_fichier'),

    url(r'^logout/$', views.LogoutView.as_view(), name='logout'),

    url(r'^login/$', views.LoginView.as_view(), name='login'),

    url(r'^document/(?P<pk>[0-9]+)/delete/$', views.SuppressionFile.as_view(), name='file-delete'),

    url(r'^api/login$', views.LoginApiView.as_view(), name='api-login'),

    url(r'^api/api-logout$', views.LogoutApiView.as_view(), name='api-logout'),
    
    url(r'^api/', include((router.urls, 'trelloBoard')))

]
