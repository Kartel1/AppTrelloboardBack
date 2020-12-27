from django.db import models
from django.contrib.auth.models import User
from login.models import Personne


class Chat(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(Personne, on_delete=models.PROTECT)
    message = models.CharField(max_length=200)

    def __str__(self):
        return self.message

# Create your models here.
