from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _

from timezones.fields import TimeZoneField

class Account(models.Model):
    
    user = models.ForeignKey(User, unique=True, verbose_name=_('user'))
    
    timezone = TimeZoneField(_('timezone'))
    language = models.CharField(_('language'), max_length=10, choices=settings.LANGUAGES, default=settings.LANGUAGE_CODE)
    
    def __unicode__(self):
        return self.user.username


class OtherServiceInfo(models.Model):
    
    # eg blogrss, twitter_user, twitter_password, pownce_user, pownce_password
    
    user = models.ForeignKey(User, verbose_name=_('user'))
    key = models.CharField(_('Other Service Info Key'), max_length=50)
    value = models.TextField(_('Other Service Info Value'))
    
    class Meta:
        unique_together = [('user', 'key')]
    
    def __unicode__(self):
        return u"%s for %s" % (self.key, self.user)

def other_service(user, key, default_value=""):
    try:
        value = OtherServiceInfo.objects.get(user=user, key=key).value
    except OtherServiceInfo.DoesNotExist:
        value = default_value
    return value


def create_account(sender, instance=None, **kwdargs):
    if instance is None:
        return
    account, created = Account.objects.get_or_create(user=instance)
    if created:
        account.save()

post_save.connect(create_account, sender=User)
