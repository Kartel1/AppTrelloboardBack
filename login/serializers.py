from rest_framework.serializers import (ModelSerializer, RelatedField, StringRelatedField, CharField)
from django.db.models.fields import EmailField, CharField
from .models import Personne, Doc
from django.contrib.auth.models import User

class UserSerializer(ModelSerializer):
    class Meta:
        model = Personne
        fields = ['id','user_infos', 'slug', 'organizations', 'trello_id', 'has_random_password']
        read_only_fields = ['id','user_infos', 'organizations', 'trello_id', 'has_random_password']


class DjangoUserSerializer(ModelSerializer):
    personne = UserSerializer(read_only=True, many = True, source='personne_set')
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email','is_active', 'is_authenticated', 'personne']
        read_only_fields = ['id', 'username', 'email','is_active', 'is_authenticated','personne']

class LoginSerializer(ModelSerializer):
    email = EmailField()
    password = CharField()
    class Meta:
        model = User
        fields = [
            'email',
            'password'
        ]
        read_only_fields = ['username','id']
        extra_kwargs = {"password":{"write_only": True}}
    
    def validate(self, data):
        
        return data