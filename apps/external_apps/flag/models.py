from datetime import datetime

from django.db import models

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from django.contrib.auth.models import User


STATUS = (
    ('1', 'flagged'),
    ('2', 'flag rejected by moderator'),
    ('3', 'creator notified'),
    ('4', 'content removed by creator'),
    ('5', 'content removed by moderator'),
)

class FlaggedContent(models.Model):
    
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    
    creator = models.ForeignKey(User, related_name="flagged_content") # user who created flagged content -- this is kept in model so it outlives content
    status = models.CharField(max_length=1, choices=STATUS, default='1')    
    moderator = models.ForeignKey(User, null=True, related_name="moderated_content") # moderator responsible for last status change


class FlagInstance(models.Model):
    
    flagged_content = models.ForeignKey(FlaggedContent)
    user = models.ForeignKey(User) # user flagging the content
    when_added = models.DateTimeField(default=datetime.now)
    when_recalled = models.DateTimeField(null=True) # if recalled at all
    comment = models.TextField() # comment by the flagger


def add_flag(flagger, content_type, object_id, content_creator, comment):
    
    # check if it's already been flagged
    try:
        flagged_content = FlaggedContent.objects.get(content_type=content_type, object_id=object_id)
    except FlaggedContent.DoesNotExist:
        flagged_content = FlaggedContent(content_type=content_type, object_id=object_id, creator=content_creator)
        flagged_content.save()
    
    flag_instance = FlagInstance(flagged_content=flagged_content, user=flagger, comment=comment)
    flag_instance.save()
    
    return flag_instance
