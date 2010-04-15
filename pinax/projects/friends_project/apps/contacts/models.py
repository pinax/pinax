from datetime import datetime

from django.db import models

from django.contrib.auth.models import User


class Contact(models.Model):
    # The user who created this contact
    owner = models.ForeignKey(User, related_name="contacts")
    
    name = models.CharField(max_length=100, blank=True)
    email = models.EmailField()
    added = models.DateField(default=datetime.now)
    
    # the user this contact ultimately corrosponds to
    user = models.ForeignKey(User, null=True)
    
    def __unicode__(self):
        return "%s (%s's contact)" % (self.email,  self.user)
