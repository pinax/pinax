from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    
    user = models.ForeignKey(User, unique=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    about = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=40, null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    
    class Admin:
        pass