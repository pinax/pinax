import datetime

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.utils.translation import ugettext as _
try:
    from hashlib import md5
except ImportError:
    from md5 import new as md5
try:
    from PIL import ImageFile
except ImportError:
    import ImageFile
try:
    from PIL import Image
except ImportError:
    import Image

AUTO_GENERATE_AVATAR_SIZES = getattr(settings, 'AUTO_GENERATE_AVATAR_SIZES', (80,))
AVATAR_RESIZE_METHOD = getattr(settings, 'AVATAR_RESIZE_METHOD', Image.ANTIALIAS)

def avatar_file_path(instance=None, filename=None, user=None):
    user = user or instance.user
    return 'avatars/%s/%s' % (user.username, filename)

class Avatar(models.Model):
    email_hash = models.CharField(max_length=128, blank=True)
    user = models.ForeignKey(User)
    primary = models.BooleanField(default=False)
    avatar = models.ImageField(max_length=1024, upload_to=avatar_file_path, blank=True)
    date_uploaded = models.DateTimeField(default=datetime.datetime.now)
    
    def __unicode__(self):
        return _(u'Avatar for %s' % self.user)
    
    def save(self, force_insert=False, force_update=False):
        self.email_hash = md5(self.user.email).hexdigest().lower()
        if self.primary:
            avatars = Avatar.objects.filter(user=self.user, primary=True).exclude(id=self.id)
            avatars.update(primary=False)
        super(Avatar, self).save(force_insert, force_update)
    
    def thumbnail_exists(self, size):
        return default_storage.exists(self.avatar_path(size))
    
    def create_thumbnail(self, size):
        orig = default_storage.open(self.avatar.path, 'rb').read()
        p = ImageFile.Parser()
        p.feed(orig)
        try:
            image = p.close()
        except IOError:
            return # What should we do here?  Render a "sorry, didn't work" img?
        (w, h) = image.size
        if w > h:
            diff = (w - h) / 2
            image = image.crop((diff, 0, w - diff, h))
        else:
            diff = (h - w) / 2
            image = image.crop((0, diff, w, h - diff))
        image = image.resize((size, size), AVATAR_RESIZE_METHOD)
        thumb = default_storage.open(self.avatar_path(size), 'wb')
        if image.mode != "RGB":
            image = image.convert("RGB")
        image.save(thumb, "JPEG")
    
    def avatar_url(self, size):
        new_url_fragment = '[%sx%s]' % (size, size)
        split = self.avatar.url.split('/')
        last = split.pop()
        last = "%s%s" % (new_url_fragment, last)
        split.append(last)
        return "/".join(split)

    def avatar_path(self, size):
        new_url_fragment = '[%sx%s]' % (size, size)
        split = self.avatar.path.split('/')
        last = split.pop()
        last = "%s%s" % (new_url_fragment, last)
        split.append(last)
        return "/".join(split)