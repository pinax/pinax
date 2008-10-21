# -*- coding: utf-8 -*-
r"""
>>> from django.contrib.auth.models import User
>>> from voting.models import Vote
>>> from voting.tests.models import Item

##########
# Voting #
##########

# Basic voting ###############################################################

>>> i1 = Item.objects.create(name='test1')
>>> users = []
>>> for username in ['u1', 'u2', 'u3', 'u4']:
...     users.append(User.objects.create_user(username, '%s@test.com' % username, 'test'))
>>> Vote.objects.get_score(i1)
{'score': 0, 'num_votes': 0}
>>> Vote.objects.record_vote(i1, users[0], +1)
>>> Vote.objects.get_score(i1)
{'score': 1, 'num_votes': 1}
>>> Vote.objects.record_vote(i1, users[0], -1)
>>> Vote.objects.get_score(i1)
{'score': -1, 'num_votes': 1}
>>> Vote.objects.record_vote(i1, users[0], 0)
>>> Vote.objects.get_score(i1)
{'score': 0, 'num_votes': 0}
>>> for user in users:
...     Vote.objects.record_vote(i1, user, +1)
>>> Vote.objects.get_score(i1)
{'score': 4, 'num_votes': 4}
>>> for user in users[:2]:
...     Vote.objects.record_vote(i1, user, 0)
>>> Vote.objects.get_score(i1)
{'score': 2, 'num_votes': 2}
>>> for user in users[:2]:
...     Vote.objects.record_vote(i1, user, -1)
>>> Vote.objects.get_score(i1)
{'score': 0, 'num_votes': 4}

>>> Vote.objects.record_vote(i1, user, -2)
Traceback (most recent call last):
    ...
ValueError: Invalid vote (must be +1/0/-1)

# Retrieval of votes #########################################################

>>> i2 = Item.objects.create(name='test2')
>>> i3 = Item.objects.create(name='test3')
>>> i4 = Item.objects.create(name='test4')
>>> Vote.objects.record_vote(i2, users[0], +1)
>>> Vote.objects.record_vote(i3, users[0], -1)
>>> Vote.objects.record_vote(i4, users[0], 0)
>>> vote = Vote.objects.get_for_user(i2, users[0])
>>> (vote.vote, vote.is_upvote(), vote.is_downvote())
(1, True, False)
>>> vote = Vote.objects.get_for_user(i3, users[0])
>>> (vote.vote, vote.is_upvote(), vote.is_downvote())
(-1, False, True)
>>> Vote.objects.get_for_user(i4, users[0]) is None
True

# In bulk
>>> votes = Vote.objects.get_for_user_in_bulk([i1, i2, i3, i4], users[0])
>>> [(id, vote.vote) for id, vote in votes.items()]
[(1, -1), (2, 1), (3, -1)]
>>> Vote.objects.get_for_user_in_bulk([], users[0])
{}

>>> for user in users[1:]:
...     Vote.objects.record_vote(i2, user, +1)
...     Vote.objects.record_vote(i3, user, +1)
...     Vote.objects.record_vote(i4, user, +1)
>>> list(Vote.objects.get_top(Item))
[(<Item: test2>, 4), (<Item: test4>, 3), (<Item: test3>, 2)]
>>> for user in users[1:]:
...     Vote.objects.record_vote(i2, user, -1)
...     Vote.objects.record_vote(i3, user, -1)
...     Vote.objects.record_vote(i4, user, -1)
>>> list(Vote.objects.get_bottom(Item))
[(<Item: test3>, -4), (<Item: test4>, -3), (<Item: test2>, -2)]

>>> Vote.objects.get_scores_in_bulk([i1, i2, i3, i4])
{1: {'score': 0, 'num_votes': 4}, 2: {'score': -2, 'num_votes': 4}, 3: {'score': -4, 'num_votes': 4}, 4: {'score': -3, 'num_votes': 3}}
>>> Vote.objects.get_scores_in_bulk([])
{}
"""
