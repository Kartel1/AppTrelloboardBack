from django.db import models


# Create your models here.
class Sprint(models.Model):
    sprint_number = models.IntegerField(db_index=True)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(auto_now_add=True)
    number_of_tasks = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return '%d: %s: %s: %d' % (self.sprint_number, self.start_date.strftime('%Y-%m-%d %H:%M'),
        self.end_date.strftime('%Y-%m-%d %H:%M'), self.number_of_tasks)


class Organization(models.Model):
    organization_trello_id = models.CharField(max_length=500, db_index=True)
    organization_name = models.CharField(max_length=200)
    

    def __str__(self):
        return '%s: %s' % (self.organization_trello_id, self.organization_name)


class Board(models.Model):
    board_name = models.CharField(max_length=200)
    board_trello_id = models.CharField(max_length=500, db_index=True)
    board_short_url = models.CharField(max_length=200)
    board_organization_id = models.ForeignKey(Organization, blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return '%s: %s: %s' % (self.board_name,self.board_trello_id,self.board_short_url)


class List(models.Model):
    board_number = models.ForeignKey(Board, on_delete=models.CASCADE)
    list_name = models.CharField(max_length=200)
    list_trello_id = models.CharField(max_length=500, db_index=True)
    creation_date = models.DateField
    closed = models.BooleanField(default=False)

    def __str__(self):
        return '%s: %s: %s: %s' % (self.list_name, self.list_trello_id,self.creation_date.strftime('%Y-%m-%d %H:%M'), self.closed)




class Card(models.Model):
    list = models.ForeignKey(List, on_delete=models.CASCADE)
    card_name = models.CharField(max_length=200)
    card_trello_id = models.CharField(max_length=500, db_index=True)
    start_processing = models.DateField(auto_now_add=True)
    effort = models.IntegerField(blank=True, null=True)
    effort_done = models.IntegerField(blank=True, null=True)
    closed = models.BooleanField(default=False)
    personnes = models.ManyToManyField('login.Personne', blank=True)
    sprint_id = models.ManyToManyField(Sprint)

    def __str__(self):
        return '%s: %s: %s: %s: %s: %s' % (self.card_name, self.card_trello_id, self.start_processing, self.effort, self.effort_done, self.closed)


class Action(models.Model):
    action_trello_id = models.CharField(max_length=500, db_index=True)
    action_name = models.CharField(max_length=200)
    board_id = models.ForeignKey(Board, on_delete=models.CASCADE)
    list_id = models.ForeignKey(List, on_delete=models.CASCADE, db_index=True)
    card_id = models.ForeignKey(Card, on_delete=models.CASCADE, db_index=True)


class Tags(models.Model):
    tag_trello_id = models.CharField(max_length=500)
    tag_name = models.CharField(max_length=200)
    card_id = models.ManyToManyField(Card)
    tag_type = models.CharField(max_length=50)

class CardTracking(models.Model):
    card = models.ForeignKey(Card,on_delete=models.CASCADE)
    effort_remaining = models.IntegerField(blank=True, null=True)
    day_of_sprint = models.IntegerField(blank=True, null=True)
    def __str__(self):
         return '%d: %d:' % (self.effort_remaining, self.day_of_sprint)