import random
from django.contrib.auth.models import User
from apps.friends.models import Friendship

def generate():
    num_users = User.objects.all().count()
    for user in User.objects.all():
        pre_friend_ids = [i['friend'].id for i in Friendship.objects.friends_for_user(user)]
        num = random.randint(0, num_users - 1)
        friends = User.objects.exclude(id__in=pre_friend_ids).order_by('?')[:num]
        for friend in friends:
            Friendship.objects.create(from_user = user, to_user = friend)
        print "Created Friendship Between %s and %s" % (user, ", ".join(map(unicode, friends)))

if __name__ == "__main__":
    generate()