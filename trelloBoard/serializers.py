from rest_framework.serializers import ModelSerializer, Serializer
from .models import (Board,
                    List,
                    Card,
                    Action,
                    Organization,
                    Sprint,
                    Tags,
                    CardTracking)
from login.models import Personne
from login.serializers import UserSerializer
from django.db.models.fields import CharField, IntegerField
   


class SprintSerializer(ModelSerializer):
    class Meta:
        model = Sprint
        fields = '__all__'

class LinkedCardSerializer(ModelSerializer):
    sprints = SprintSerializer(read_only=True, many=True, source='sprint')
    class Meta:
        model = Card
        fields = ['card_name','card_trello_id' ,'start_processing', 'effort', 'effort_done','closed','sprints']

class LinkedListSerializer(ModelSerializer):
    cards = LinkedCardSerializer(read_only=True, many=True, source='card_set')
    class Meta:
        model = List
        fields = ['id','list_name','list_trello_id','closed','cards']


class LinkedBoardSerializer(ModelSerializer):
    lists = LinkedListSerializer(read_only=True, many=True, source='list_set')
    class Meta:
        model = Board
        fields = ['board_name', 'board_trello_id','board_short_url','lists']

class OrganizationSerializer(ModelSerializer):
    boards = LinkedBoardSerializer(read_only=True, many=True, source='board_set')
    class Meta:
        model = Organization
        fields = ['organization_trello_id','organization_name','boards']

class PersonneTrelloTabInfosSerializer(ModelSerializer):
    organizations = OrganizationSerializer(read_only=True, many=True)
    class Meta:
        model = Personne
        fields = ['id','user_infos', 'trello_id','organizations']



class SlugSerializer(Serializer):
    slug = CharField()
    def validate(self, data):
        return data


class Serbo(ModelSerializer):
    class Meta:
        model = Board
        fields = ['board_name']

class SerLi(ModelSerializer):
    board = Serbo(read_only =True, source='board_number')
    class Meta:
        model = List
        fields = ['list_name','board']



class TestSerCard(ModelSerializer):
    list = SerLi(read_only = True)
    sprint = SprintSerializer(read_only=True, source='sprint_id', many=True)
    class Meta:
        model = Card
        fields = ['card_name','card_trello_id' ,'start_processing', 'effort', 'effort_done','closed', 'list', 'sprint']


class SerPer(ModelSerializer):
    card = TestSerCard(read_only = True, source='card_set', many=True)
    class Meta:
        model = Personne
        fields = ['id', 'card']

class BurnDownInfo(Serializer):
    slug = CharField()
    sprint_value = IntegerField()
    sprint_day = IntegerField()
    def validate(self, data):
        return data


class SerCardTracking(ModelSerializer):
   class Meta:
        model = CardTracking
        fields = ['effort_remaining', 'day_of_sprint' ]


class SerCard(ModelSerializer):
    class Meta:
        model = Card
        fields = ['card_name','card_trello_id' ,'start_processing', 'effort', 'effort_done','closed']

class SerBurnDown(ModelSerializer):
    cardtracking = SerCardTracking(read_only=True,source='cardtracking_set',many=True)
    class Meta:
        model = Card
        fields = ['card_name','card_trello_id' ,'start_processing', 'effort', 'effort_done','closed', 'cardtracking']

# class TestSerBurnDown(ModelSerializer):
#      card = SerCard(read_only=True)
#      class Meta:
#         model = CardTracking
#         fields = ['effort_remaining', 'day_of_sprint','card']