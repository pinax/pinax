from django.core.urlresolvers import reverse
from django.contrib.auth.models import  User
from django.utils.translation import ugettext_lazy as _
from django.db import models

from groups.base import Group

class BasicGroup(Group):
    
    members = models.ManyToManyField(User, related_name='basic_groups', verbose_name=_('members'))
    
    def get_absolute_url(self):
        return reverse('group_detail', kwargs={'group_slug': self.slug})
    
    def get_url_kwargs(self):
        return {'group_slug': self.slug}