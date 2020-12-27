import re
import json

from django.http import JsonResponse

from .models import *
from requests_oauthlib import OAuth1Session
from webapp import settings
from django.contrib.auth.models import User
from login.models import Personne


class TrelloBoardAjaxMixins(object):

    def post(self, request):
        if request.is_ajax() and request.user.is_authenticated and 'oauth_token' in request.session:
            pattern_size = re.compile('^size\\s*(s|S|m|M|l|L|xl|XL)$')
            pattern_spring = re.compile('^sprint\\s*[0-9]{1,3}$')
            pattern_spring_number = re.compile('^sprint\\s*')
            organisation_list = Organization.objects.all()
            for item_organisation in organisation_list:
                person_url = 'https://api.trello.com/1/organizations/'+ item_organisation.organization_trello_id  +'/members'
                person_auth = OAuth1Session(settings.TRELLO_AUTH_KEY,
                                      client_secret=settings.TRELLO_AUTH_SECRET,
                                      resource_owner_key=request.session.get('oauth_token')[0],
                                      resource_owner_secret=request.session['oauth_token_secret'])
                person_response = person_auth.get(person_url)                          
                json_person_response = json.loads(person_response.text)
                for person in json_person_response:
                    if not Personne.objects.filter(trello_id = person['id']).exists():
                        member_url = 'https://api.trello.com/1/members/'+ person['id']
                        member_auth = OAuth1Session(settings.TRELLO_AUTH_KEY,
                                      client_secret=settings.TRELLO_AUTH_SECRET,
                                      resource_owner_key=request.session.get('oauth_token')[0],
                                      resource_owner_secret=request.session['oauth_token_secret'])
                        member_response = person_auth.get(member_url)                          
                        json_member_response = json.loads(member_response.text)

                        password = User.objects.make_random_password()
                        user = User.objects.create_user(person['fullName'], json_member_response['email'], password)
                        user.personne_set.create(user_logo='Anonymous.png', slug=person['fullName'].replace(' ', '-'),
                                            trello_id=person['id'])

                url = "https://api.trello.com/1/organizations/" + item_organisation.organization_trello_id + "/boards"
                oauth = OAuth1Session(settings.TRELLO_AUTH_KEY,
                                      client_secret=settings.TRELLO_AUTH_SECRET,
                                      resource_owner_key=request.session.get('oauth_token')[0],
                                      resource_owner_secret=request.session['oauth_token_secret'])
                response = oauth.get(url)
                list_in_response_board = json.loads(response.text)
                for itemBoard in list_in_response_board:
                    Board.objects.update_or_create(board_name=itemBoard['name'], board_trello_id=itemBoard['id'],
                                                   board_short_url=itemBoard['shortUrl'],
                                                   board_organization_id=item_organisation)

                    url = "https://api.trello.com/1/boards/" + itemBoard['id'] + "/lists"
                    response = oauth.get(url)
                    list_in_response_list = json.loads(response.text)
                    for itemList in list_in_response_list:
                        List.objects.update_or_create(board_number=Board.objects.get(board_trello_id=itemBoard['id']),
                                                      list_name=itemList['name'], list_trello_id=itemList['id'])

                    url = "https://api.trello.com/1/boards/" + itemBoard['id'] + "/cards"
                    response = oauth.get(url)
                    list_in_response_card = json.loads(response.text)
                    for itemCard in list_in_response_card:
                        card = Card.objects.update_or_create(list=List.objects.get(list_trello_id=itemCard['idList']),
                                                             card_name=itemCard['name'], card_trello_id=itemCard['id'],
                                                             closed=itemCard['closed'])
                        for member in itemCard['idMembers']:
                            card[0].personnes.add(Personne.objects.get(trello_id=member))
                        for label in itemCard['labels']:
                            if re.match(pattern_size, label['name']):
                                tag = Tags.objects.update_or_create(tag_trello_id=label['id'], tag_name=label['name'],
                                                                    tag_type='Size')
                                tag[0].card_id.add(Card.objects.get(card_trello_id=card[0].card_trello_id))
                            elif re.match(pattern_spring, label['name']):
                                tag = Tags.objects.update_or_create(tag_trello_id=label['id'], tag_name=label['name'],
                                                                    tag_type='Sprint')
                                tag[0].card_id.add(Card.objects.get(card_trello_id=card[0].card_trello_id))
                for tag in Tags.objects.filter(tag_type='Sprint').distinct('tag_type'):
                    Sprint.objects.update_or_create(
                        sprint_number=re.sub(pattern_spring_number, '', tag.tag_name),
                        number_of_tasks=0)
                for tag in Tags.objects.filter(tag_type='Sprint'):
                    cards = tag.card_id.all()
                    for card in cards:
                        card.sprint_id.add(
                            Sprint.objects.get(sprint_number=re.sub(pattern_spring_number, '', tag.tag_name)))

                return JsonResponse(self.sucess)
            else:
                response = JsonResponse(self.fail)
                response.status_code = 498
                return response
