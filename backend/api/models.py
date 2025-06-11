from typing import Iterable
from django.db import models
from django.db.models.manager import Manager
from django.contrib.auth.models import AbstractUser
from api.addons.functions import *

import datetime

# Create your models here.


class CustomUser(AbstractUser):
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    credentials = models.CharField(max_length=120, blank=True)

    objects: Manager = models.Manager()

    def __str__(self) -> str:
        return self.username


class SocialMediaType(models.Model):
    type = models.CharField(max_length=120, unique=True)
    image = models.ImageField(upload_to='mediatype/')

    objects: Manager = models.Manager()

    def __str__(self):
        return self.type


class SocialMedia(models.Model):
    type = models.ForeignKey(SocialMediaType, on_delete=models.CASCADE)
    reference = models.CharField(max_length=120, unique=True)
    date_to = models.DateTimeField(editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    objects: Manager = models.Manager()

    def save(self, *args, **kwargs):
        self.date_to = datetime.datetime.now() + datetime.timedelta(days=365)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.reference


class Group(models.Model):
    name = models.CharField(max_length=120, unique=True, editable=False)
    invitation = models.TextField(unique=True, editable=False)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    objects: Manager = models.Manager()

    # def save(self, *args, **kwargs):
    #     if not self.pk:
    #         super().save(*args, **kwargs)

    #     self.name = f'group - {self.pk}'
    #     self.invitation = generate_invite_code(self.name)

    #     super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class Legacy(models.Model):
    name = models.CharField(max_length=60, unique=True)

    objects: Manager = models.Manager()

    def __str__(self) -> str:
        return self.name


class CharacterClass(models.Model):
    name = models.CharField(max_length=80, unique=True)
    image = models.ImageField(upload_to='classes/')

    objects: Manager = models.Manager()

    def __str__(self) -> str:
        return self.name


class Character(models.Model):
    name = models.CharField(max_length=60, unique=True)
    clas = models.ForeignKey(CharacterClass, on_delete=models.CASCADE)
    gear_score = models.DecimalField(max_digits=10, decimal_places=2)
    legacy = models.ForeignKey(Legacy, on_delete=models.CASCADE)

    objects: Manager = models.Manager()

    def __str__(self) -> str:
        return self.name


class Privilege():
    OWNER = 'owner'
    EDITOR = 'editor'
    PARTICIPANT = 'participant'

    CHOICES = [
        (OWNER, 'владелец'),
        (EDITOR, 'редактор'),
        (PARTICIPANT, 'участник')
    ]


class GroupCharacters(models.Model):
    character = models.ForeignKey(Legacy, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    objects: Manager = models.Manager()


class GroupParticipants(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    privilege = models.CharField(
        max_length=40,
        choices=Privilege.CHOICES,
        default=Privilege.PARTICIPANT
    )
    character = models.ForeignKey(Legacy, on_delete=models.CASCADE)

    objects: Manager = models.Manager()


class NotificationStatus:
    ACCEPTED = 'accepted'
    DECLINED = 'declined'
    WAITING = 'waiting'

    CHOICES = [
        (ACCEPTED, 'Принято'),
        (DECLINED, 'Отклонено'),
        (WAITING, 'Ожидание'),
    ]


class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    character = models.ForeignKey(Legacy, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20,
        choices=NotificationStatus.CHOICES,
        default=NotificationStatus.WAITING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects: Manager = models.Manager()


class RaidType(models.Model):
    name = models.CharField(max_length=50)

    objects: Manager = models.Manager()

    def __str__(self) -> str:
        return self.name


class RaidDifficulty(models.Model):
    name = models.CharField(max_length=50)

    objects: Manager = models.Manager()

    def __str__(self) -> str:
        return self.name


class Raid(models.Model):
    name = models.CharField(max_length=120)
    type = models.ForeignKey(RaidType, on_delete=models.CASCADE)
    difficulty = models.ForeignKey(
        RaidDifficulty, on_delete=models.CASCADE, blank=True, default=None)
    release_date = models.DateField(auto_now_add=True, editable=False)
    gs = models.IntegerField()
    capacity = models.IntegerField()

    objects: Manager = models.Manager()

    def __str__(self) -> str:
        return self.name


class RaidGroup(models.Model):
    raid = models.ForeignKey(Raid, on_delete=models.CASCADE)
    character = models.ForeignKey(Characters, on_delete=models.CASCADE)
    position = models.IntegerField()

    objects: Manager = models.Manager()


class Item(models.Model):
    name = models.CharField(max_length=120)
    image = models.ImageField(upload_to='items/')

    objects: Manager = models.Manager()

    def __str__(self) -> str:
        return self.name


class RaidReward(models.Model):
    raid = models.ForeignKey(Raid, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    count = models.IntegerField()

    objects: Manager = models.Manager()
