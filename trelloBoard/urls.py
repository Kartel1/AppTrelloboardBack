from django.conf.urls import url, include

from . import views

app_name = 'trelloBoard'

urlpatterns = [
    url(r'^trelloBoard/infos/$', views.GetBoardView.as_view(), name='infos'),
    url(r'^trelloBoard/update/$', views.TestUpdate.as_view(), name='update'),
    url(r'^trelloBoard/get-api-token/$', views.GetApiToken.as_view(), name='refresh'),
    url(r'^trelloBoard/end-get-credentials/$', views.EndRetrieveCredentials.as_view(), name='reroot'),
    url(r'^api/trello-api-get-token/$', views.GetApiTokenView.as_view(), name='trello-token'),
    url(r'^api/end-get-token/$', views.EndRetrieveCredentialsApiView.as_view(), name='end-trello-token'),
    url(r'^api/get-personne-tab-infos/(?P<slug>[\w-]+)/$', views.GetPersonneTrelloTabInfosView.as_view(), name='personne-tab-infos'),
    url(r'^api/set-card-effort/$', views.SetEffort.as_view(), name='set-card-effort'),
    url(r'^api/get-burndown/$',views.GetBurnDown.as_view(),name='get-burndown'),
    url(r'^api/get-sprints/$',views.GetSprints.as_view(),name='get-sprints'),
]


