import random
from pinax.profiles.models import Profile
from django.contrib.auth.models import User
from django.contrib.webdesign.lorem_ipsum import words
from django.template.defaultfilters import capfirst
from timezones.forms import TIMEZONE_CHOICES

RSS_FEEDS = (
    'http://www.scripting.com/rss.xml',
    'http://feedproxy.google.com/TechCrunch',
    'http://feeds.feedburner.com/ommalik',
    'http://feedproxy.google.com/fastcompany/scobleizer?format=xml',
    'http://www.djangoproject.com/rss/community/',
)

def generate():
    for user in User.objects.all():
        profile, created = Profile.objects.get_or_create(user = user,
            defaults=dict(
                name = user.get_full_name(),
                about = capfirst(words(8, common=False)) + '.',
# @@@ need to move these to account fixtures
#                blogrss = random.choice(RSS_FEEDS),
#                timezone = random.choice(TIMEZONE_CHOICES)[0],
            ),
        )
        print "Created User Profile: %s" % (profile,)

if __name__ == "__main__":
    generate()