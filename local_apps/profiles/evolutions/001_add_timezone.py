
from django_evolution.mutations import *
from django.db import models
from django.conf import settings

MUTATIONS = [
    AddField('Profile', 'timezone', models.CharField, initial=settings.TIME_ZONE, max_length=100)
]
