import json
import re

from django.http import HttpResponseRedirect, Http404, JsonResponse
from django.shortcuts import redirect
from django.views import generic
from django.views.generic import RedirectView, ListView
from django.views.generic.base import ContextMixin
from django.core.mail import send_mail
from django.contrib.auth.models import User
from requests_oauthlib import OAuth1Session
from login.models import Personne

from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView , RetrieveAPIView, UpdateAPIView
from rest_framework.authentication import BasicAuthentication

from django.contrib.auth import login, authenticate
from django.db.models import Prefetch, FilteredRelation, Q

from webapp import settings
from .models import *
from .mixins import TrelloBoardAjaxMixins
from .serializers import(PersonneTrelloTabInfosSerializer, 
                        SlugSerializer,
                        TestSerCard,
                        LinkedCardSerializer,
                        SerCardTracking,
                        BurnDownInfo,
                        SerBurnDown,
                        SprintSerializer)
from login.serializers import UserSerializer


# Create your views here.


class GetBoardView(generic.ListView):
    template_name = 'trelloBoard/info.html'
    context_object_name = 'all_boards'

    def get_context_data(self, *args, **kwargs):
        context = super(GetBoardView, self).get_context_data(*args, **kwargs)
        context['all_sprints'] = Sprint.objects.all()
        context['all_organizations'] = Organization.objects.all()
        return context

    def get_queryset(self):
        return Board.objects.all()


class GetApiToken(RedirectView, ContextMixin):

    def get(self, request, *args, **kwargs):
        request_url = "https://trello.com/1/OAuthGetRequestToken"
        authorize_url = "https://trello.com/1/OAuthAuthorizeToken"
        client = OAuth1Session(settings.TRELLO_AUTH_KEY, client_secret=settings.TRELLO_AUTH_SECRET,
                               callback_uri='http://127.0.0.1:8000/trelloBoard/end-get-credentials/')
        fetch_response = client.fetch_request_token(request_url)
        request.session['oauth_token_temp'] = fetch_response.get('oauth_token')
        request.session['oauth_token_secret_temp'] = fetch_response.get('oauth_token_secret')
        settings.authorize_url = client.authorization_url(authorize_url, name='testTrelloBoard',
                                                          scope='read,account')
        return HttpResponseRedirect(settings.authorize_url)


class EndRetrieveCredentials(RedirectView):

    def get(self, request, *args, **kwargs):
        access_url = "https://trello.com/1/OAuthGetAccessToken"
        verifier = request.GET['oauth_verifier']
        oauth = OAuth1Session(settings.TRELLO_AUTH_KEY,
                              client_secret=settings.TRELLO_AUTH_SECRET,
                              resource_owner_key=request.session['oauth_token_temp'],
                              resource_owner_secret=request.session['oauth_token_secret_temp'],
                              verifier=verifier)

        oauth_final_tokens = oauth.fetch_access_token(access_url)
        request.session['oauth_token'] = oauth_final_tokens.get('oauth_token'),
        request.session['oauth_token_secret'] = oauth_final_tokens.get('oauth_token_secret')
        url = 'https://api.trello.com/1/members/me'
        oauth = OAuth1Session(settings.TRELLO_AUTH_KEY,
                              client_secret=settings.TRELLO_AUTH_SECRET,
                              resource_owner_key=request.session.get('oauth_token')[0],
                              resource_owner_secret=request.session['oauth_token_secret'])
        response = oauth.get(url)
        json_response = json.loads(response.text)
        request.session['user_name'] = json_response['fullName']
        request.session['user_id'] = json_response['id']
        # request.session['user_organisations_id'] = json_response['idOrganizations']
        for itemOrganisations in json_response['idOrganizations']:
            org_url = 'https://api.trello.com/1/organizations/' + itemOrganisations
            org_oauth = OAuth1Session(settings.TRELLO_AUTH_KEY,
                                      client_secret=settings.TRELLO_AUTH_SECRET,
                                      resource_owner_key=request.session.get('oauth_token')[0],
                                      resource_owner_secret=request.session['oauth_token_secret'])
            org_response = org_oauth.get(org_url)
            json_org_response = json.loads(org_response.text)
            Organization.objects.update_or_create(organization_trello_id=itemOrganisations,
                                                  defaults={'organization_name': json_org_response['displayName']})
        if Personne.objects.filter(trello_id=json_response['id']).exists():
            personne = Personne.objects.get(slug=json_response['fullName'].replace(' ', '-'),
                                            trello_id=json_response['id'])
            try:
                user = User.objects.get(pk=personne.usager.pk)
                if user.email != json_response['email'] and json_response['email'] is not None:
                    user.email = json_response['email']
                    user.save()
                if user is not None and user.is_active:
                    login(request, user)
            except User.DoesNotExist:
                password = User.objects.make_random_password()
                user = User.objects.create_user(json_response['fullName'], json_response['email'], password)
                if user is not None and user.is_active:
                    login(request, user)
        else:
            password = User.objects.make_random_password()
            user = User.objects.create_user(json_response['fullName'], json_response['email'], password)
            user.personne_set.create(user_logo='Anonymous.png', slug=json_response['fullName'].replace(' ', '-'),
                                     trello_id=json_response['id'])
            if user is not None and user.is_active:
                login(request, user)
                # send_mail('Your Password for TrelloBoard App',
                #           'Your password is : ' + password,
                #           settings.EMAIL_HOST_USER,
                #           [user.email],
                #           fail_silently=False)

        return redirect('login:connexion')


class TestUpdate(ListView, TrelloBoardAjaxMixins):
    sucess = {
        'message': 'Successfully updated'
    }
    fail = {
        'message': 'Fail to update'
    }
    # def post(self, request):
    # if request.is_ajax() and request.user.is_authenticated and 'oauth_token' in request.session:
    #     pattern_size = re.compile('^size\\s*(s|S|m|M|l|L|xl|XL)$')
    #     pattern_spring = re.compile('^sprint\\s*[0-9]{1,3}$')
    #     pattern_spring_number = re.compile('^sprint\\s*')
    #     url = "https://api.trello.com/1/organizations/" + request.session.get('user_organisations_id')[
    #         0] + "/boards"
    #     oauth = OAuth1Session(settings.TRELLO_AUTH_KEY,
    #                           client_secret=settings.TRELLO_AUTH_SECRET,
    #                           resource_owner_key=request.session.get('oauth_token')[0],
    #                           resource_owner_secret=request.session['oauth_token_secret'])
    #     response = oauth.get(url)
    #     list_in_response_board = json.loads(response.text)
    #     for itemBoard in list_in_response_board:
    #         Board.objects.update_or_create(board_name=itemBoard['name'], board_trello_id=itemBoard['id'],
    #                                        board_short_url=itemBoard['shortUrl'],
    #                                        board_organization_id=itemBoard['idOrganization'])
    #
    #         url = "https://api.trello.com/1/boards/" + itemBoard['id'] + "/lists"
    #         response = oauth.get(url)
    #         list_in_response_list = json.loads(response.text)
    #         for itemList in list_in_response_list:
    #             List.objects.update_or_create(board_number=Board.objects.get(board_trello_id=itemBoard['id']),
    #                                           list_name=itemList['name'], list_trello_id=itemList['id'])
    #
    #         url = "https://api.trello.com/1/boards/" + itemBoard['id'] + "/cards"
    #         response = oauth.get(url)
    #         list_in_response_card = json.loads(response.text)
    #         for itemCard in list_in_response_card:
    #             Card.objects.update_or_create(list=List.objects.get(list_trello_id=itemCard['idList']),
    #                                           card_name=itemCard['name'], card_trello_id=itemCard['id'],
    #                                           closed=itemCard['closed'])
    #             for label in itemCard['labels']:
    #                 if re.match(pattern_size, label['name']):
    #                     Tags.objects.update_or_create(tag_trello_id=label['id'], tag_name=label['name'],
    #                                                   card_id=Card.objects.get(card_trello_id=itemCard['id']),
    #                                                   tag_type='Size')
    #                 elif re.match(pattern_spring, label['name']):
    #                     Tags.objects.update_or_create(tag_trello_id=label['id'], tag_name=label['name'],
    #                                                   card_id=Card.objects.get(card_trello_id=itemCard['id']),
    #                                                   tag_type='Sprint')
    #     for tag in Tags.objects.filter(tag_type='Sprint').distinct('tag_type'):
    #         Sprint.objects.update_or_create(sprint_number=re.sub(pattern_spring_number, '', tag.tag_name),
    #                                         number_of_tasks=Tags.objects.filter(tag_name=tag.tag_name).count())
    #         data = {
    #             'message': 'Successfully updated'
    #         }
    #     return JsonResponse(data)
    # else:
    #     data = {
    #         'message': 'Fail to update'
    #     }
    #     response = JsonResponse(data)
    #     response.status_code = 401
    #     return response

class GetApiTokenView(APIView, ContextMixin):
    serializer_class = None
    def get(self, request, *args, **kwargs):
        user = authenticate(username='devllu_kartel', password='qkUtnUZRRt')
        if user is not None or request.session['user_id'] is not None:
            login(request, user)
        request_url = "https://trello.com/1/OAuthGetRequestToken"
        authorize_url = "https://trello.com/1/OAuthAuthorizeToken"
        client = OAuth1Session(settings.TRELLO_AUTH_KEY, client_secret=settings.TRELLO_AUTH_SECRET,
                               callback_uri='http://localhost:4200/home')
        fetch_response = client.fetch_request_token(request_url)
        settings.oauth_token_temp = fetch_response.get('oauth_token')
        settings.oauth_token_secret_temp = fetch_response.get('oauth_token_secret')
        settings.authorize_url = client.authorization_url(authorize_url, name='testTrelloBoard',
                                                          scope='read,account')
        # return HttpResponseRedirect(settings.authorize_url)
        return Response(data=settings.authorize_url, status=HTTP_200_OK)

class EndRetrieveCredentialsApiView(APIView):
    serializer_class = None
    def post(self, request, *args, **kwargs):
        user = authenticate(username='devllu_kartel', password='qkUtnUZRRt')
        if user is not None or request.session['user_id'] is not None:
            login(request, user)
        access_url = "https://trello.com/1/OAuthGetAccessToken"
        verifier = request.data['oauth_verifier']
        oauth = OAuth1Session(settings.TRELLO_AUTH_KEY,
                              client_secret=settings.TRELLO_AUTH_SECRET,
                              resource_owner_key=settings.oauth_token_temp,
                              resource_owner_secret=settings.oauth_token_secret_temp,
                              verifier=verifier)

        oauth_final_tokens = oauth.fetch_access_token(access_url)
        settings.oauth_token = oauth_final_tokens.get('oauth_token'),
        settings.oauth_token_secret = oauth_final_tokens.get('oauth_token_secret')
        url = 'https://api.trello.com/1/members/me'
        oauth = OAuth1Session(settings.TRELLO_AUTH_KEY,
                              client_secret=settings.TRELLO_AUTH_SECRET,
                              resource_owner_key=settings.oauth_token[0],
                              resource_owner_secret=settings.oauth_token_secret)
        response = oauth.get(url)
        json_response = json.loads(response.text)
        request.session['user_name'] = json_response['fullName']
        request.session['user_id'] = json_response['id']
        # request.session['user_organisations_id'] = json_response['idOrganizations']
        for itemOrganisations in json_response['idOrganizations']:
            org_url = 'https://api.trello.com/1/organizations/' + itemOrganisations
            org_oauth = OAuth1Session(settings.TRELLO_AUTH_KEY,
                                      client_secret=settings.TRELLO_AUTH_SECRET,
                                      resource_owner_key=settings.oauth_token[0],
                                      resource_owner_secret=settings.oauth_token_secret)
            org_response = org_oauth.get(org_url)
            json_org_response = json.loads(org_response.text)
            Organization.objects.update_or_create(organization_trello_id=itemOrganisations,
                                                  defaults={'organization_name': json_org_response['displayName']})
        if Personne.objects.filter(trello_id=json_response['id']).exists():
            personne = Personne.objects.get(slug=json_response['fullName'].replace(' ', '-'),
                                            trello_id=json_response['id'])
            try:
                user = User.objects.get(pk=personne.usager.pk)
                if user.email != json_response['email'] and json_response['email'] is not None:
                    user.email = json_response['email']
                    user.save()
                if user is not None and user.is_active:
                    login(request, user)
            except User.DoesNotExist:
                password = User.objects.make_random_password()
                user = User.objects.create_user(json_response['fullName'], json_response['email'], password)
                if user is not None and user.is_active:
                    login(request, user)
        else:
            password = User.objects.make_random_password()
            user = User.objects.create_user(json_response['fullName'], json_response['email'], password)
            user.personne_set.create(user_logo='Anonymous.png', slug=json_response['fullName'].replace(' ', '-'),
                                     trello_id=json_response['id'])
            if user is not None and user.is_active:
                login(request, user)
                # send_mail('Your Password for TrelloBoard App',
                #           'Your password is : ' + password,
                #           settings.EMAIL_HOST_USER,
                #           [user.email],
                #           fail_silently=False)

        return Response(status=HTTP_200_OK)

class GetPersonneTrelloTabInfosView(RetrieveAPIView):
    serializer_class = SlugSerializer
    queryset = ''
    lookup_field = 'slug'
    lookup_url_kwarg = 'slug'
    def get(self, request, *args, **kwargs):
        # data = request.data
        # serializer = SlugSerializer(data=data)
        # if serializer.is_valid(raise_exception=True):
        """ obj = Personne.objects.prefetch_related('organizations',
                'organizations__board_set','organizations__board_set__list_set',
                'organizations__board_set__list_set__card_set',
                'organizations__board_set__list_set__card_set__sprint_id').get(slug=data['slug']) """
        # obj = Personne.objects.prefetch_related('card_set','card_set__list','card_set__list__board_number','card_set__sprint_id').get(slug=self.kwargs['slug'])
        # obj = Personne.objects.prefetch_related(Prefetch('card_set', queryset=Card.objects.filter(sprint_id__sprint_number=23)),'card_set__list','card_set__list__board_number','card_set__sprint_id').get(slug=self.kwargs['slug'])
        obj = Card.objects.prefetch_related('list', 'list__board_number','sprint_id').filter(personnes__slug = self.kwargs['slug'])
        data_response = TestSerCard(instance = obj, many=True).data
        return Response(data=data_response, status=HTTP_200_OK)
    # return Response(status=HTTP_400_BAD_REQUEST)

class SetEffort(UpdateAPIView):
    serializer_class = LinkedCardSerializer
    queryset = ''
    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = LinkedCardSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            obj = Card.objects.get(card_trello_id=data['card_trello_id'])
            obj.effort = data['effort']
            obj.effort_done = data['effort_done']
            obj.save()
            """ data_response = TestSerCard(instance = obj.card_set, many=True).data """
            return Response(data='', status=HTTP_200_OK)
        return Response(status=HTTP_400_BAD_REQUEST)

class GetBurnDown(ListAPIView):
    serializer_class = BurnDownInfo
    queryset = ''
    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = BurnDownInfo(data=data)
        if serializer.is_valid(raise_exception=True):
            obj= Card.objects.prefetch_related(Prefetch('cardtracking_set',queryset=CardTracking.objects.filter(card__personnes__slug=data['slug'],day_of_sprint__lt=data['sprint_day']))).filter(personnes__slug=data['slug'], sprint_id__sprint_number=data['sprint_value'])
            data_response = SerBurnDown(obj, many= True).data
            return Response(data=data_response, status=HTTP_200_OK)
        return Response(status=HTTP_400_BAD_REQUEST)

class GetSprints(ListAPIView):
    serializer_class = SprintSerializer
    queryset = Sprint.objects.order_by('-start_date')
    # def get(self, request, *args, **kwargs):
    #     obj = Sprint.objects.all()
    #     data_response = SprintSerializer(obj, many=True).data
    #     return Response(data=data_response, status=HTTP_200_OK)

# class GetBurnDown(ListAPIView):
#     serializer_class = BurnDownInfo
#     queryset = ''
#     def post(self, request, *args, **kwargs):
#         data = request.data
#         serializer = BurnDownInfo(data=data)
#         if serializer.is_valid(raise_exception=True):
#             obj= CardTracking.objects.select_related('card').filter(card__personnes__slug=data['slug'],day_of_sprint__lt=data['sprint_day'],card__sprint_id__sprint_number=data['sprint_value'])
#             data_response = TestSerBurnDown(instance = obj, many=True).data
#             return Response(data=data_response, status=HTTP_200_OK)
#         return Response(status=HTTP_400_BAD_REQUEST)
