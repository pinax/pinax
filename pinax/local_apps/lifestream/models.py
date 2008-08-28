from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

SERVICES_CHOIECS = ((1,'Twitter'),
                    (2,'Pownce')),

class Comment(models.Model):
    """
    LifeSteram Comment
    """
    on = models.IntegerField('ID of the post')
    service =  models.IntegerField(choices = SERVICES_CHOIECS)
    by = models.ForeignKey(User)
    content = models.TextField(_('Comment Content'))
    def __str__(self):
        return self.by
    class Admin:
        pass
        
class Vote(models.Model):
    """
    Vote for 
    """
    for_user = models.ForeignKey(User, related_name = 'for_user')
    from_service = models.IntegerField(choices=SERVICES_CHOIECS)
    content = models.TextField(_('Post Content'))
    voted = models.ManyToManyField(User, blank = True, null = True, related_name = 'votes_for')
    comments = models.ManyToManyField(User, blank = True, null = True, related_name = 'comments_on')
    def __str__(self):
        return self.for_user
    class Admin:
        pass
        
    