from django.db import models
from django.urls import reverse
from trelloBoard.models import Organization
from django.contrib.auth.models import User


class Personne(models.Model):
    usager = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    user_infos = models.CharField(max_length=1000)
    user_logo = models.FileField()
    slug = models.SlugField(unique=True)
    organizations = models.ManyToManyField(Organization)
    trello_id = models.CharField(max_length=500, db_index=True)
    has_random_password = models.BooleanField(default=True)

    def __str__(self):
        return '%s: %s: %s: %s' % (self.user_infos, self.slug, self.organizations, self.trello_id)

    def get_absolute_url(self):
        return reverse('login:detail', kwargs={'slug': self.slug})


class Doc(models.Model):
    utilisateur = models.ForeignKey(Personne, on_delete=models.CASCADE)
    fichier_titre = models.CharField(max_length=500)
    fichier_description = models.CharField(max_length=1000)
    fichier_file = models.FileField()
    is_favorite = models.BooleanField(default=False)
    date = models.DateField(auto_now_add=True)

    def get_absolute_url(self):
        return reverse('login:detail', kwargs={'slug': self.utilisateur.slug})

    def __str__(self):
        return self.fichier_titre
