import random

from django.contrib.auth.models import User
from django.contrib.webdesign.lorem_ipsum import words
from django.template.defaultfilters import capfirst

from microblogging.models import Tweet

OEMBED_CONTENT = [
    'http://www.youtube.com/watch?v=_RyodnisVvU&feature=rec-fresh',
    'http://revision3.com/tekzilla/superhot/',
    'http://www.viddler.com/explore/pop17/videos/93/',
] + ([''] * 50)

def generate():
    for user in User.objects.all():
        for num_tweets in xrange(random.randint(1, 50)):
            num_words = random.randint(1, 100)
            content = words(num_words, common=False)
            oembed = random.choice(OEMBED_CONTENT)
            split_num = random.randint(0, len(content) - 1)
            content = capfirst('%s %s %s' % (content[:split_num], oembed,
                content[split_num:]))[:139] + '.'
            Tweet.objects.create(
                sender=user,
                text=content
            )
        print "Created %s Tweets from User: %s" % (num_tweets, user)

if __name__ == "__main__":
    generate()