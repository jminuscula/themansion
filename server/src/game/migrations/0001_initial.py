# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-13 09:28
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Ability',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, unique=True)),
                ('description', models.CharField(max_length=512)),
                ('action_phase', models.CharField(choices=[('voting', 'VOTING'), ('day', 'DAY'), ('startgame', 'STARTGAME'), ('room', 'ROOM'), ('night', 'NIGHT')], max_length=16, null=True)),
            ],
            options={
                'verbose_name_plural': 'abilities',
            },
        ),
        migrations.CreateModel(
            name='Character',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alive', models.BooleanField(default=True)),
                ('turns_to_die', models.IntegerField(blank=True, null=True)),
                ('hidden', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='CharacterAbility',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('available', models.BooleanField(default=True)),
                ('ability', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='game.Ability')),
                ('character', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='game.Character')),
            ],
            options={
                'verbose_name_plural': 'character abilities',
            },
        ),
        migrations.CreateModel(
            name='CharacterObjective',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('points', models.IntegerField(default=0)),
                ('complete', models.BooleanField(default=False)),
                ('character', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='game.Character')),
            ],
        ),
        migrations.CreateModel(
            name='CharacterWeapon',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ammo', models.IntegerField(null=True)),
                ('character', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='game.Character')),
            ],
        ),
        migrations.CreateModel(
            name='Day',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('night_turns', models.IntegerField(default=3)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='games_owned', to=settings.AUTH_USER_MODEL)),
                ('current_day', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='current_day', to='game.Day')),
            ],
        ),
        migrations.CreateModel(
            name='GameMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('received_on', models.DateTimeField(auto_now_add=True)),
                ('character', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='messages', to='game.Character')),
                ('current_day', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='game.Day')),
            ],
        ),
        migrations.CreateModel(
            name='GameRoom',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_open', models.BooleanField(default=True)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rooms', to='game.Game')),
            ],
            options={
                'default_related_name': 'rooms',
            },
        ),
        migrations.CreateModel(
            name='Kill',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('killed', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='deaths', to='game.Character')),
                ('killer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='kills', to='game.Character')),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='killings', to='game.GameRoom')),
                ('weapon', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='game.CharacterWeapon')),
            ],
        ),
        migrations.CreateModel(
            name='Night',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField(default=0)),
                ('turns_left', models.IntegerField()),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='nights', to='game.Game')),
            ],
        ),
        migrations.CreateModel(
            name='NightAction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('attack_blank', 'ATTACK_BLANK'), ('move', 'MOVE'), ('attack_defend', 'ATTACK_DEFEND'), ('attack_kill', 'ATTACK_KILL'), ('special', 'SPECIAL'), ('open_door', 'OPEN_DOOR'), ('close_door', 'CLOSE_DOOR'), ('pick_weapon', 'PICK_WEAPON')], max_length=32)),
                ('confirmed', models.BooleanField(default=False)),
                ('character', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='night_turns', to='game.Character')),
                ('character_target', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='game.Character')),
                ('night', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='actions', to='game.Night')),
                ('room_target', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='game.GameRoom')),
            ],
        ),
        migrations.CreateModel(
            name='Objective',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True)),
                ('description', models.CharField(max_length=256)),
                ('trigger', models.CharField(choices=[('terrorized', 'TERRORIZED'), ('execute', 'EXECUTE'), ('kill', 'KILL'), ('killed', 'KILLED'), ('terrorize', 'TERRORIZE'), ('endgame', 'ENDGAME'), ('dead', 'DEAD'), ('executed', 'EXECUTED')], max_length=16)),
                ('points', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Persona',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True)),
                ('title', models.CharField(max_length=64)),
                ('bio', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True)),
                ('room_type', models.CharField(choices=[('dormitory', 'DORMITORY'), ('library', 'LIBRARY'), ('observatory', 'OBSERVATORY'), ('basic', 'BASIC'), ('basement', 'BASEMENT'), ('kitchen', 'KITCHEN'), ('hall', 'HALL')], max_length=16)),
                ('closeable', models.BooleanField(default=True)),
                ('connections', models.ManyToManyField(blank=True, related_name='passages', related_query_name='connected_with', to='game.Room')),
            ],
        ),
        migrations.CreateModel(
            name='Terror',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ghost', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='terrorizations', to='game.Character')),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='game.Room')),
                ('terrorized', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='terrors', to='game.Character')),
            ],
        ),
        migrations.CreateModel(
            name='Weapon',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=16, unique=True)),
                ('description', models.CharField(max_length=256)),
                ('weapon_type', models.CharField(choices=[('stunt', 'STUNT'), ('knife', 'KNIFE'), ('poison', 'POISON'), ('gun', 'GUN')], max_length=16)),
                ('max_ammo', models.IntegerField(blank=True, null=True)),
                ('starting_ammo', models.IntegerField(blank=True, null=True)),
                ('resource', models.BooleanField(default=False)),
                ('intention', models.BooleanField(default=True)),
                ('effect_turns', models.IntegerField(blank=True, null=True)),
                ('starting_room', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='game.Room')),
            ],
        ),
        migrations.AddField(
            model_name='nightaction',
            name='weapon_target',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='game.Weapon'),
        ),
        migrations.AddField(
            model_name='gameroom',
            name='room',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rooms', to='game.Room'),
        ),
        migrations.AddField(
            model_name='gameroom',
            name='weapons',
            field=models.ManyToManyField(blank=True, related_name='rooms', to='game.Weapon'),
        ),
        migrations.AddField(
            model_name='gamemessage',
            name='current_night',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='game.Night'),
        ),
        migrations.AddField(
            model_name='gamemessage',
            name='current_room',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='game.GameRoom'),
        ),
        migrations.AddField(
            model_name='game',
            name='current_night',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='current_night', to='game.Night'),
        ),
        migrations.AddField(
            model_name='game',
            name='game_rooms',
            field=models.ManyToManyField(through='game.GameRoom', to='game.Room'),
        ),
        migrations.AddField(
            model_name='day',
            name='game',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='days', to='game.Game'),
        ),
        migrations.AddField(
            model_name='characterweapon',
            name='picked_at',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='game.GameRoom'),
        ),
        migrations.AddField(
            model_name='characterweapon',
            name='weapon',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='game.Weapon'),
        ),
        migrations.AddField(
            model_name='characterobjective',
            name='objective',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='game.Objective'),
        ),
        migrations.AddField(
            model_name='character',
            name='abilities',
            field=models.ManyToManyField(through='game.CharacterAbility', to='game.Ability'),
        ),
        migrations.AddField(
            model_name='character',
            name='current_room',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='players_here', to='game.GameRoom'),
        ),
        migrations.AddField(
            model_name='character',
            name='game',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='characters', to='game.Game'),
        ),
        migrations.AddField(
            model_name='character',
            name='objectives',
            field=models.ManyToManyField(through='game.CharacterObjective', to='game.Objective'),
        ),
        migrations.AddField(
            model_name='character',
            name='persona',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='game.Persona'),
        ),
        migrations.AddField(
            model_name='character',
            name='player',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='character',
            name='weapons',
            field=models.ManyToManyField(through='game.CharacterWeapon', to='game.Weapon'),
        ),
        migrations.AddField(
            model_name='ability',
            name='room',
            field=models.ManyToManyField(blank=True, to='game.Room'),
        ),
        migrations.AlterUniqueTogether(
            name='kill',
            unique_together=set([('killer', 'killed')]),
        ),
        migrations.AlterUniqueTogether(
            name='gameroom',
            unique_together=set([('game', 'room')]),
        ),
        migrations.AlterUniqueTogether(
            name='characterobjective',
            unique_together=set([('character', 'objective')]),
        ),
        migrations.AlterUniqueTogether(
            name='characterability',
            unique_together=set([('character', 'ability')]),
        ),
    ]
