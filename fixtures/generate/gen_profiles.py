from profiles.models import Profile
from django.contrib.auth.models import User
from django.contrib.webdesign.lorem_ipsum import words
from django.template.defaultfilters import capfirst

def generate():
    for user in User.objects.all():
        profile, created = Profile.objects.get_or_create(user = user,
            defaults=dict(
                name=user.get_full_name(),
                about=capfirst(words(8, common=False)) + '.',
            ),
        )
        print "Created User Profile: %s" % (profile,)

if __name__ == "__main__":
    generate()