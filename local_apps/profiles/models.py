from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _

from timezones.fields import TimeZoneField

class Profile(models.Model):

    user = models.ForeignKey(User, unique=True, verbose_name=_('user'))
    name = models.CharField(_('name'), max_length=50, null=True, blank=True)
    about = models.TextField(_('about'), null=True, blank=True)
    location = models.CharField(_('location'), max_length=40, null=True, blank=True)
    website = models.URLField(_('website'), null=True, blank=True, verify_exists=False)
    
    # @@@ the following are all deprecated -  see account/models.py
    blogrss = models.URLField(_('blog rss/atom'), null=True, blank=True, verify_exists=False)
    timezone = TimeZoneField(_('timezone'))
    twitter_user = models.CharField(_('Twitter Username'), max_length=50, blank=True)
    twitter_password = models.CharField(_('Twitter Password'), max_length=50, blank=True)
    pownce_user = models.CharField(_('Pownce Username'), max_length=50, blank=True)
    pownce_password = models.CharField(_('Pownce Password'), max_length=50, blank=True)
    language = models.CharField(_('language'), max_length=10, choices=settings.LANGUAGES, default=settings.LANGUAGE_CODE)
    
    def __unicode__(self):
        return self.user.username
    
    class Meta:
        verbose_name = _('profile')
        verbose_name_plural = _('profiles')

def create_profile(sender, instance=None, **kwdargs):
    if instance is None: return
    profile, created = Profile.objects.get_or_create(user=instance)
    if created: profile.save()

post_save.connect(create_profile, sender=User)
