"""

Note: these tests depend on Pinax/projects.

>>> from swaps.models import *
>>> from django.contrib.auth.models import User

>>> bob = User(username='bob')
>>> bob.save()
>>> alice = User(username='alice')
>>> alice.save()

>>> offer1 = Offer(
...     offerer=bob,
...     short_description='test offer',
...     offering='something good',
...     want='something better')
>>> offer1.save()
>>> offer2 = Offer(
...     offerer=alice,
...     short_description='another test offer',
...     offering='something better',
...     want='whatever')
>>> offer2.save()

>>> offer3 = Offer(
...     offerer=alice,
...     short_description='yet another test offer',
...     offering='something worse',
...     want='nothing')
>>> offer3.save()


>>> swap1 = Swap(
...     proposing_offer=offer1,
...     responding_offer=offer2)
>>> swap1.save()

>>> swap1.state
1

>>> swap1.proposing_offer.state
2

Don't know why this one needs an int while the others don't
>>> int(swap1.responding_offer.state)
1

>>> swap2 = Swap(
...     proposing_offer=offer3,
...     responding_offer=offer2)
>>> swap2.save()

>>> swap1 = Swap.objects.get(pk=1)
>>> swap1.accept()
>>> swap1.save()

>>> swap1 = Swap.objects.get(pk=1)
>>> int(swap1.state)
2

>>> int(swap1.proposing_offer.state)
3
>>> int(swap1.responding_offer.state)
3

>>> swap2 = Swap.objects.get(pk=2)
>>> int(swap2.state)
6
>>> int(swap2.proposing_offer.state)
1

>>> swap2.conflicted_by.pk
1

"""