from datetime import datetime

from django.db import models

from django.contrib.auth.models import User

from emailconfirmation.models import EmailConfirmation
from emailconfirmation.signals import email_confirmed


class Contact(models.Model):
    # The user who created this contact
    owner = models.ForeignKey(User, related_name="contacts")
    
    name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(db_index=True)
    added = models.DateField(default=datetime.now)
    
    # the user this contact ultimately corrosponds to
    user = models.ForeignKey(User, null=True)


def link_to_contacts(sender, instance=None, **kwargs):
    email_address = kwargs.get("email_address")
    # update all Contact instances which match the verified e-mail
    Contact.objects.filter(email=email_address.email).update(user=email_address.user)
email_confirmed.connect(link_to_contacts, sender=EmailConfirmation)