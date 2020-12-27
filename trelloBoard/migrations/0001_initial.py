# Generated by Django 3.0.6 on 2020-11-29 15:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('login', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Board',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('board_name', models.CharField(max_length=200)),
                ('board_trello_id', models.CharField(db_index=True, max_length=500)),
                ('board_short_url', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Card',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('card_name', models.CharField(max_length=200)),
                ('card_trello_id', models.CharField(db_index=True, max_length=500)),
                ('start_processing', models.DateField(auto_now_add=True)),
                ('effort', models.IntegerField(blank=True, null=True)),
                ('effort_done', models.IntegerField(blank=True, null=True)),
                ('closed', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('organization_trello_id', models.CharField(db_index=True, max_length=500)),
                ('organization_name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Sprint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sprint_number', models.IntegerField(db_index=True)),
                ('start_date', models.DateField(auto_now_add=True)),
                ('end_date', models.DateField(auto_now_add=True)),
                ('number_of_tasks', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Tags',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag_trello_id', models.CharField(max_length=500)),
                ('tag_name', models.CharField(max_length=200)),
                ('tag_type', models.CharField(max_length=50)),
                ('card_id', models.ManyToManyField(to='trelloBoard.Card')),
            ],
        ),
        migrations.CreateModel(
            name='List',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('list_name', models.CharField(max_length=200)),
                ('list_trello_id', models.CharField(db_index=True, max_length=500)),
                ('closed', models.BooleanField(default=False)),
                ('board_number', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trelloBoard.Board')),
            ],
        ),
        migrations.CreateModel(
            name='CardTracking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('effort_remaining', models.IntegerField(blank=True, null=True)),
                ('day_of_sprint', models.IntegerField(blank=True, null=True)),
                ('card', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trelloBoard.Card')),
            ],
        ),
        migrations.AddField(
            model_name='card',
            name='list',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trelloBoard.List'),
        ),
        migrations.AddField(
            model_name='card',
            name='personnes',
            field=models.ManyToManyField(blank=True, to='login.Personne'),
        ),
        migrations.AddField(
            model_name='card',
            name='sprint_id',
            field=models.ManyToManyField(to='trelloBoard.Sprint'),
        ),
        migrations.AddField(
            model_name='board',
            name='board_organization_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='trelloBoard.Organization'),
        ),
        migrations.CreateModel(
            name='Action',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action_trello_id', models.CharField(db_index=True, max_length=500)),
                ('action_name', models.CharField(max_length=200)),
                ('board_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trelloBoard.Board')),
                ('card_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trelloBoard.Card')),
                ('list_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trelloBoard.List')),
            ],
        ),
    ]