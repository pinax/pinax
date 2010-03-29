from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import  User

from groups.base import Group



class Tribe(Group):
    
    members = models.ManyToManyField(User,
        related_name = "tribes",
        verbose_name = _("members")
    )
    
    def get_absolute_url(self):
        return reverse("tribe_detail", kwargs={"group_slug": self.slug})
