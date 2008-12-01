import random

from django.contrib.auth.models import User
from django.contrib.webdesign.lorem_ipsum import words

from friends.models import Friendship, FriendshipInvitation

def generate():
    num_users = User.objects.all().count()
    for user in User.objects.all():
        pre_friend_ids = [i['friend'].id for i in Friendship.objects.friends_for_user(user)]
        num = random.randint(1, (num_users - 1) / 10)
        friends = User.objects.exclude(id__in=pre_friend_ids).order_by('?')[:num]
        for friend in friends:
            num_words = random.randint(1, 100)
            message = words(num_words, common=False)
            ji = FriendshipInvitation.objects.create(
                from_user=user,
                to_user=friend,
                message=message,
                status='2'
            )
            ji.accept()
        print "Created Friendship Between %s and %d others." % (user, len(friends))

if __name__ == "__main__":
    generate()