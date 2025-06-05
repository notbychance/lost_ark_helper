from typing import Iterable
from django.db import models
from django.db.models.manager import Manager
from django.contrib.auth.models import AbstractUser
from api.addons.functions import *

import datetime

# Create your models here.


class Group(models.Model):
    name = models.CharField(max_length=120, unique=True, editable=False)
    invitation = models.TextField(unique=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.pk:
            super().save(*args, **kwargs)

        self.name = f'group - {self.pk}'
        self.invitation = generate_invite_code(self.name)

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class CustomUser(AbstractUser):
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    is_leader = models.BooleanField(default=False)
    is_gamer = models.BooleanField(default=True)
    credentials = models.CharField(max_length=120, blank=True)
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, blank=True, default=None)

    def save(self, *args, **kwargs):
        if self.is_superuser or self.is_staff:
            self.is_leader = True

        if self.is_leader:
            self.is_gamer = False
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.username


class SocialMediaType(models.Model):
    type = models.CharField(max_length=120, unique=True)
    image = models.ImageField(upload_to='mediatype/')

    objects: Manager = models.Manager()

    def __str__(self):
        return self.type


class SocialMedia(models.Model):
    media_type = models.ForeignKey(SocialMediaType, on_delete=models.CASCADE)
    reference = models.CharField(max_length=120, unique=True)
    date_to = models.DateTimeField(editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    objects: Manager = models.Manager()

    def save(self, *args, **kwargs):
        self.date_to = datetime.datetime.now() + datetime.timedelta(days=365)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.reference


class UserCharacter(models.Model):
    name = models.CharField(max_length=40, unique=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    objects: Manager = models.Manager()

    def __str__(self) -> str:
        return self.name


class CharactersClass(models.Model):
    name = models.CharField(max_length=80, unique=True)
    image = models.ImageField(upload_to='classes/')

    objects: Manager = models.Manager()

    def __str__(self) -> str:
        return self.name


class Characters(models.Model):
    name = models.CharField(max_length=40, unique=True)
    clas = models.ForeignKey(CharactersClass, on_delete=models.CASCADE)
    gear_score = models.DecimalField(max_digits=10, decimal_places=2)

    objects: Manager = models.Manager()

    def __str__(self) -> str:
        return self.name


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

    objects: Manager = models.Manager()

    def __str__(self) -> str:
        return self.name


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
