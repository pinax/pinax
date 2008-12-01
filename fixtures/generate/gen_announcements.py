import random

from django.contrib.auth.models import User
from django.contrib.webdesign.lorem_ipsum import words
from django.template.defaultfilters import capfirst

from announcements.models import Announcement

def generate():
    for i in xrange(random.randint(1, 10)):
        announcement = Announcement.objects.create(
            title=capfirst(words(8, common=False)),
            content=words(random.randint(1, 1000), common=False),
            creator=User.objects.order_by('?')[0],
            site_wide=random.random() > 0.5,
            members_only=random.random() > 0.5
        )
        print "Created Announcement: %s" % (announcement,)

if __name__ == "__main__":
    generate()