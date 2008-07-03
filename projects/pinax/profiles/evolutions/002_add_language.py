from django_evolution.mutations import *
from django.db import models
from django.conf import settings

MUTATIONS = [
    AddField('Profile', 'language', models.CharField, initial=settings.LANGUAGE_CODE, max_length=10)
]
