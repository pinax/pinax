# -*- coding: utf-8 -*-
tests = r"""
>>> import os
>>> from django import newforms as forms
>>> from tagging.forms import TagField
>>> from tagging import settings
>>> from tagging.models import Tag, TaggedItem
>>> from tagging.tests.models import Article, Link, Perch, Parrot, FormTest
>>> from tagging.utils import calculate_cloud, get_tag_list, get_tag, parse_tag_input
>>> from tagging.utils import LINEAR
>>> from tagging.validators import is_tag_list, is_tag

#############
# Utilities #
#############

# Tag input ###################################################################

# Simple space-delimited tags
>>> parse_tag_input('one')
[u'one']
>>> parse_tag_input('one two')
[u'one', u'two']
>>> parse_tag_input('one two three')
[u'one', u'three', u'two']
>>> parse_tag_input('one one two two')
[u'one', u'two']

# Comma-delimited multiple words - an unquoted comma in the input will trigger
# this.
>>> parse_tag_input(',one')
[u'one']
>>> parse_tag_input(',one two')
[u'one two']
>>> parse_tag_input(',one two three')
[u'one two three']
>>> parse_tag_input('a-one, a-two and a-three')
[u'a-one', u'a-two and a-three']

# Double-quoted multiple words - a completed quote will trigger this.
# Unclosed quotes are ignored.
>>> parse_tag_input('"one')
[u'one']
>>> parse_tag_input('"one two')
[u'one', u'two']
>>> parse_tag_input('"one two three')
[u'one', u'three', u'two']
>>> parse_tag_input('"one two"')
[u'one two']
>>> parse_tag_input('a-one "a-two and a-three"')
[u'a-one', u'a-two and a-three']

# No loose commas - split on spaces
>>> parse_tag_input('one two "thr,ee"')
[u'one', u'thr,ee', u'two']

# Loose commas - split on commas
>>> parse_tag_input('"one", two three')
[u'one', u'two three']

# Double quotes can contain commas
>>> parse_tag_input('a-one "a-two, and a-three"')
[u'a-one', u'a-two, and a-three']
>>> parse_tag_input('"two", one, one, two, "one"')
[u'one', u'two']

# Bad users! Naughty users!
>>> parse_tag_input(None)
[]
>>> parse_tag_input('')
[]
>>> parse_tag_input('"')
[]
>>> parse_tag_input('""')
[]
>>> parse_tag_input('"' * 7)
[]
>>> parse_tag_input(',,,,,,')
[]
>>> parse_tag_input('",",",",",",","')
[u',']
>>> parse_tag_input('a-one "a-two" and "a-three')
[u'a-one', u'a-three', u'a-two', u'and']

# Normalised Tag list input ###################################################
>>> cheese = Tag.objects.create(name='cheese')
>>> toast = Tag.objects.create(name='toast')
>>> get_tag_list(cheese)
[<Tag: cheese>]
>>> get_tag_list('cheese toast')
[<Tag: cheese>, <Tag: toast>]
>>> get_tag_list('cheese,toast')
[<Tag: cheese>, <Tag: toast>]
>>> get_tag_list([])
[]
>>> get_tag_list(['cheese', 'toast'])
[<Tag: cheese>, <Tag: toast>]
>>> get_tag_list([cheese.id, toast.id])
[<Tag: cheese>, <Tag: toast>]
>>> get_tag_list(['cheese', 'toast', 'ŠĐĆŽćžšđ'])
[<Tag: cheese>, <Tag: toast>]
>>> get_tag_list([cheese, toast])
[<Tag: cheese>, <Tag: toast>]
>>> get_tag_list((cheese, toast))
(<Tag: cheese>, <Tag: toast>)
>>> get_tag_list(Tag.objects.filter(name__in=['cheese', 'toast']))
[<Tag: cheese>, <Tag: toast>]
>>> get_tag_list(['cheese', toast])
Traceback (most recent call last):
    ...
ValueError: If a list or tuple of tags is provided, they must all be tag names, Tag objects or Tag ids.
>>> get_tag_list(29)
Traceback (most recent call last):
    ...
ValueError: The tag input given was invalid.

# Normalised Tag input
>>> get_tag(cheese)
<Tag: cheese>
>>> get_tag('cheese')
<Tag: cheese>
>>> get_tag(cheese.id)
<Tag: cheese>
>>> get_tag('mouse')

# Tag clouds ##################################################################
>>> tags = []
>>> for line in open(os.path.join(os.path.dirname(__file__), 'tags.txt')).readlines():
...     name, count = line.rstrip().split()
...     tag = Tag(name=name)
...     tag.count = int(count)
...     tags.append(tag)

>>> sizes = {}
>>> for tag in calculate_cloud(tags, steps=5):
...     sizes[tag.font_size] = sizes.get(tag.font_size, 0) + 1

# This isn't a pre-calculated test, just making sure it's consistent
>>> sizes
{1: 48, 2: 30, 3: 19, 4: 15, 5: 10}

>>> sizes = {}
>>> for tag in calculate_cloud(tags, steps=5, distribution=LINEAR):
...     sizes[tag.font_size] = sizes.get(tag.font_size, 0) + 1

# This isn't a pre-calculated test, just making sure it's consistent
>>> sizes
{1: 97, 2: 12, 3: 7, 4: 2, 5: 4}

>>> calculate_cloud(tags, steps=5, distribution='cheese')
Traceback (most recent call last):
    ...
ValueError: Invalid distribution algorithm specified: cheese.

# Validators ##################################################################

>>> is_tag_list('foo qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbn bar', {})
Traceback (most recent call last):
    ...
ValidationError: [u'Each tag may be no more than 50 characters long.']

>>> is_tag('"test"', {})
>>> is_tag(',test', {})
>>> is_tag('f o o', {})
Traceback (most recent call last):
    ...
ValidationError: [u'Multiple tags were given.']
>>> is_tag_list('foo qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbn bar', {})
Traceback (most recent call last):
    ...
ValidationError: [u'Each tag may be no more than 50 characters long.']

###########
# Tagging #
###########

# Basic tagging ###############################################################

>>> dead = Parrot.objects.create(state='dead')
>>> Tag.objects.update_tags(dead, 'foo,bar,"ter"')
>>> Tag.objects.get_for_object(dead)
[<Tag: bar>, <Tag: foo>, <Tag: ter>]
>>> Tag.objects.update_tags(dead, '"foo" bar "baz"')
>>> Tag.objects.get_for_object(dead)
[<Tag: bar>, <Tag: baz>, <Tag: foo>]
>>> Tag.objects.add_tag(dead, 'foo')
>>> Tag.objects.get_for_object(dead)
[<Tag: bar>, <Tag: baz>, <Tag: foo>]
>>> Tag.objects.add_tag(dead, 'zip')
>>> Tag.objects.get_for_object(dead)
[<Tag: bar>, <Tag: baz>, <Tag: foo>, <Tag: zip>]
>>> Tag.objects.add_tag(dead, '    ')
Traceback (most recent call last):
    ...
AttributeError: No tags were given: "    ".
>>> Tag.objects.add_tag(dead, 'one two')
Traceback (most recent call last):
    ...
AttributeError: Multiple tags were given: "one two".

# Note that doctest in Python 2.4 (and maybe 2.5?) doesn't support non-ascii
# characters in output, so we're displaying the repr() here.
>>> Tag.objects.update_tags(dead, 'ŠĐĆŽćžšđ')
>>> repr(Tag.objects.get_for_object(dead))
'[<Tag: \xc5\xa0\xc4\x90\xc4\x86\xc5\xbd\xc4\x87\xc5\xbe\xc5\xa1\xc4\x91>]'

>>> Tag.objects.update_tags(dead, None)
>>> Tag.objects.get_for_object(dead)
[]

# Using a model's TagField
>>> f1 = FormTest.objects.create(tags=u'test3 test2 test1')
>>> Tag.objects.get_for_object(f1)
[<Tag: test1>, <Tag: test2>, <Tag: test3>]
>>> f1.tags = u'test4'
>>> f1.save()
>>> Tag.objects.get_for_object(f1)
[<Tag: test4>]
>>> f1.tags = ''
>>> f1.save()
>>> Tag.objects.get_for_object(f1)
[]

# Forcing tags to lowercase
>>> settings.FORCE_LOWERCASE_TAGS = True
>>> Tag.objects.update_tags(dead, 'foO bAr Ter')
>>> Tag.objects.get_for_object(dead)
[<Tag: bar>, <Tag: foo>, <Tag: ter>]
>>> Tag.objects.update_tags(dead, 'foO bAr baZ')
>>> Tag.objects.get_for_object(dead)
[<Tag: bar>, <Tag: baz>, <Tag: foo>]
>>> Tag.objects.add_tag(dead, 'FOO')
>>> Tag.objects.get_for_object(dead)
[<Tag: bar>, <Tag: baz>, <Tag: foo>]
>>> Tag.objects.add_tag(dead, 'Zip')
>>> Tag.objects.get_for_object(dead)
[<Tag: bar>, <Tag: baz>, <Tag: foo>, <Tag: zip>]
>>> Tag.objects.update_tags(dead, None)
>>> f1.tags = u'TEST5'
>>> f1.save()
>>> Tag.objects.get_for_object(f1)
[<Tag: test5>]
>>> f1.tags
u'test5'

# Retrieving tags by Model ####################################################

>>> Tag.objects.usage_for_model(Parrot)
[]
>>> parrot_details = (
...     ('pining for the fjords', 9, True,  'foo bar'),
...     ('passed on',             6, False, 'bar baz ter'),
...     ('no more',               4, True,  'foo ter'),
...     ('late',                  2, False, 'bar ter'),
... )

>>> for state, perch_size, perch_smelly, tags in parrot_details:
...     perch = Perch.objects.create(size=perch_size, smelly=perch_smelly)
...     parrot = Parrot.objects.create(state=state, perch=perch)
...     Tag.objects.update_tags(parrot, tags)

>>> [(tag.name, tag.count) for tag in Tag.objects.usage_for_model(Parrot, counts=True)]
[(u'bar', 3), (u'baz', 1), (u'foo', 2), (u'ter', 3)]
>>> [(tag.name, tag.count) for tag in Tag.objects.usage_for_model(Parrot, min_count=2)]
[(u'bar', 3), (u'foo', 2), (u'ter', 3)]

# Limiting results to a subset of the model
>>> [(tag.name, tag.count) for tag in Tag.objects.usage_for_model(Parrot, counts=True, filters=dict(state='no more'))]
[(u'foo', 1), (u'ter', 1)]
>>> [(tag.name, tag.count) for tag in Tag.objects.usage_for_model(Parrot, counts=True, filters=dict(state__startswith='p'))]
[(u'bar', 2), (u'baz', 1), (u'foo', 1), (u'ter', 1)]
>>> [(tag.name, tag.count) for tag in Tag.objects.usage_for_model(Parrot, counts=True, filters=dict(perch__size__gt=4))]
[(u'bar', 2), (u'baz', 1), (u'foo', 1), (u'ter', 1)]
>>> [(tag.name, tag.count) for tag in Tag.objects.usage_for_model(Parrot, counts=True, filters=dict(perch__smelly=True))]
[(u'bar', 1), (u'foo', 2), (u'ter', 1)]
>>> [(tag.name, tag.count) for tag in Tag.objects.usage_for_model(Parrot, min_count=2, filters=dict(perch__smelly=True))]
[(u'foo', 2)]
>>> [(tag.name, hasattr(tag, 'counts')) for tag in Tag.objects.usage_for_model(Parrot, filters=dict(perch__size__gt=4))]
[(u'bar', False), (u'baz', False), (u'foo', False), (u'ter', False)]
>>> [(tag.name, hasattr(tag, 'counts')) for tag in Tag.objects.usage_for_model(Parrot, filters=dict(perch__size__gt=99))]
[]

# Related tags
>>> [(tag.name, tag.count) for tag in Tag.objects.related_for_model(Tag.objects.filter(name__in=['bar']), Parrot, counts=True)]
[(u'baz', 1), (u'foo', 1), (u'ter', 2)]
>>> [(tag.name, tag.count) for tag in Tag.objects.related_for_model(Tag.objects.filter(name__in=['bar']), Parrot, min_count=2)]
[(u'ter', 2)]
>>> [tag.name for tag in Tag.objects.related_for_model(Tag.objects.filter(name__in=['bar']), Parrot, counts=False)]
[u'baz', u'foo', u'ter']
>>> [(tag.name, tag.count) for tag in Tag.objects.related_for_model(Tag.objects.filter(name__in=['bar', 'ter']), Parrot, counts=True)]
[(u'baz', 1)]
>>> [(tag.name, tag.count) for tag in Tag.objects.related_for_model(Tag.objects.filter(name__in=['bar', 'ter', 'baz']), Parrot, counts=True)]
[]

# Once again, with feeling (strings)
>>> [(tag.name, tag.count) for tag in Tag.objects.related_for_model('bar', Parrot, counts=True)]
[(u'baz', 1), (u'foo', 1), (u'ter', 2)]
>>> [(tag.name, tag.count) for tag in Tag.objects.related_for_model('bar', Parrot, min_count=2)]
[(u'ter', 2)]
>>> [tag.name for tag in Tag.objects.related_for_model('bar', Parrot, counts=False)]
[u'baz', u'foo', u'ter']
>>> [(tag.name, tag.count) for tag in Tag.objects.related_for_model(['bar', 'ter'], Parrot, counts=True)]
[(u'baz', 1)]
>>> [(tag.name, tag.count) for tag in Tag.objects.related_for_model(['bar', 'ter', 'baz'], Parrot, counts=True)]
[]

# Retrieving tagged objects by Model ##########################################

>>> foo = Tag.objects.get(name='foo')
>>> bar = Tag.objects.get(name='bar')
>>> baz = Tag.objects.get(name='baz')
>>> ter = Tag.objects.get(name='ter')
>>> TaggedItem.objects.get_by_model(Parrot, foo)
[<Parrot: no more>, <Parrot: pining for the fjords>]
>>> TaggedItem.objects.get_by_model(Parrot, bar)
[<Parrot: late>, <Parrot: passed on>, <Parrot: pining for the fjords>]

# Intersections are supported
>>> TaggedItem.objects.get_by_model(Parrot, [foo, baz])
[]
>>> TaggedItem.objects.get_by_model(Parrot, [foo, bar])
[<Parrot: pining for the fjords>]
>>> TaggedItem.objects.get_by_model(Parrot, [bar, ter])
[<Parrot: late>, <Parrot: passed on>]

# Issue 114 - Intersection with non-existant tags
>>> TaggedItem.objects.get_intersection_by_model(Parrot, [])
[]

# You can also pass Tag QuerySets
>>> TaggedItem.objects.get_by_model(Parrot, Tag.objects.filter(name__in=['foo', 'baz']))
[]
>>> TaggedItem.objects.get_by_model(Parrot, Tag.objects.filter(name__in=['foo', 'bar']))
[<Parrot: pining for the fjords>]
>>> TaggedItem.objects.get_by_model(Parrot, Tag.objects.filter(name__in=['bar', 'ter']))
[<Parrot: late>, <Parrot: passed on>]

# You can also pass strings and lists of strings
>>> TaggedItem.objects.get_by_model(Parrot, 'foo baz')
[]
>>> TaggedItem.objects.get_by_model(Parrot, 'foo bar')
[<Parrot: pining for the fjords>]
>>> TaggedItem.objects.get_by_model(Parrot, 'bar ter')
[<Parrot: late>, <Parrot: passed on>]
>>> TaggedItem.objects.get_by_model(Parrot, ['foo', 'baz'])
[]
>>> TaggedItem.objects.get_by_model(Parrot, ['foo', 'bar'])
[<Parrot: pining for the fjords>]
>>> TaggedItem.objects.get_by_model(Parrot, ['bar', 'ter'])
[<Parrot: late>, <Parrot: passed on>]

# Issue 50 - Get by non-existent tag
>>> TaggedItem.objects.get_by_model(Parrot, 'argatrons')
[]

# Unions
>>> TaggedItem.objects.get_union_by_model(Parrot, ['foo', 'ter'])
[<Parrot: late>, <Parrot: no more>, <Parrot: passed on>, <Parrot: pining for the fjords>]
>>> TaggedItem.objects.get_union_by_model(Parrot, ['bar', 'baz'])
[<Parrot: late>, <Parrot: passed on>, <Parrot: pining for the fjords>]

# Issue 114 - Union with non-existant tags
>>> TaggedItem.objects.get_union_by_model(Parrot, [])
[]

# Retrieving related objects by Model #########################################

# Related instances of the same Model
>>> l1 = Link.objects.create(name='link 1')
>>> Tag.objects.update_tags(l1, 'tag1 tag2 tag3 tag4 tag5')
>>> l2 = Link.objects.create(name='link 2')
>>> Tag.objects.update_tags(l2, 'tag1 tag2 tag3')
>>> l3 = Link.objects.create(name='link 3')
>>> Tag.objects.update_tags(l3, 'tag1')
>>> l4 = Link.objects.create(name='link 4')
>>> TaggedItem.objects.get_related(l1, Link)
[<Link: link 2>, <Link: link 3>]
>>> TaggedItem.objects.get_related(l1, Link, num=1)
[<Link: link 2>]
>>> TaggedItem.objects.get_related(l4, Link)
[]

# Limit related items
>>> TaggedItem.objects.get_related(l1, Link.objects.exclude(name='link 3'))
[<Link: link 2>]

# Related instance of a different Model
>>> a1 = Article.objects.create(name='article 1')
>>> Tag.objects.update_tags(a1, 'tag1 tag2 tag3 tag4')
>>> TaggedItem.objects.get_related(a1, Link)
[<Link: link 1>, <Link: link 2>, <Link: link 3>]
>>> Tag.objects.update_tags(a1, 'tag6')
>>> TaggedItem.objects.get_related(a1, Link)
[]

################
# Model Fields #
################

# TagField ####################################################################

# Ensure that automatically created forms use TagField
>>> class TestForm(forms.ModelForm):
...     class Meta:
...         model = FormTest
>>> form = TestForm()
>>> form.fields['tags'].__class__.__name__
'TagField'

# Recreating string representaions of tag lists ###############################
>>> plain = Tag.objects.create(name='plain')
>>> spaces = Tag.objects.create(name='spa ces')
>>> comma = Tag.objects.create(name='com,ma')

>>> from tagging.utils import edit_string_for_tags
>>> edit_string_for_tags([plain])
u'plain'
>>> edit_string_for_tags([plain, spaces])
u'plain, spa ces'
>>> edit_string_for_tags([plain, spaces, comma])
u'plain, spa ces, "com,ma"'
>>> edit_string_for_tags([plain, comma])
u'plain "com,ma"'
>>> edit_string_for_tags([comma, spaces])
u'"com,ma", spa ces'

###############
# Form Fields #
###############

>>> t = TagField()
>>> t.clean('foo')
u'foo'
>>> t.clean('foo bar baz')
u'foo bar baz'
>>> t.clean('foo,bar,baz')
u'foo,bar,baz'
>>> t.clean('foo, bar, baz')
u'foo, bar, baz'
>>> t.clean('foo qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvb bar')
u'foo qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvb bar'
>>> t.clean('foo qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbn bar')
Traceback (most recent call last):
    ...
ValidationError: [u'Each tag may be no more than 50 characters long.']
"""

tests_pre_qsrf = tests + r"""
# Limiting results to a queryset
>>> Tag.objects.usage_for_queryset(Parrot.objects.filter())
Traceback (most recent call last):
    ...
AttributeError: 'TagManager.usage_for_queryset' is not compatible with pre-queryset-refactor versions of Django.
"""

tests_post_qsrf = tests + r"""
>>> from django.db.models import Q

# Limiting results to a queryset
>>> [(tag.name, tag.count) for tag in Tag.objects.usage_for_queryset(Parrot.objects.filter(state='no more'), counts=True)]
[(u'foo', 1), (u'ter', 1)]
>>> [(tag.name, tag.count) for tag in Tag.objects.usage_for_queryset(Parrot.objects.filter(state__startswith='p'), counts=True)]
[(u'bar', 2), (u'baz', 1), (u'foo', 1), (u'ter', 1)]
>>> [(tag.name, tag.count) for tag in Tag.objects.usage_for_queryset(Parrot.objects.filter(perch__size__gt=4), counts=True)]
[(u'bar', 2), (u'baz', 1), (u'foo', 1), (u'ter', 1)]
>>> [(tag.name, tag.count) for tag in Tag.objects.usage_for_queryset(Parrot.objects.filter(perch__smelly=True), counts=True)]
[(u'bar', 1), (u'foo', 2), (u'ter', 1)]
>>> [(tag.name, tag.count) for tag in Tag.objects.usage_for_queryset(Parrot.objects.filter(perch__smelly=True), min_count=2)]
[(u'foo', 2)]
>>> [(tag.name, hasattr(tag, 'counts')) for tag in Tag.objects.usage_for_queryset(Parrot.objects.filter(perch__size__gt=4))]
[(u'bar', False), (u'baz', False), (u'foo', False), (u'ter', False)]
>>> [(tag.name, hasattr(tag, 'counts')) for tag in Tag.objects.usage_for_queryset(Parrot.objects.filter(perch__size__gt=99))]
[]
>>> [(tag.name, tag.count) for tag in Tag.objects.usage_for_queryset(Parrot.objects.filter(Q(perch__size__gt=6) | Q(state__startswith='l')), counts=True)]
[(u'bar', 2), (u'foo', 1), (u'ter', 1)]
>>> [(tag.name, tag.count) for tag in Tag.objects.usage_for_queryset(Parrot.objects.filter(Q(perch__size__gt=6) | Q(state__startswith='l')), min_count=2)]
[(u'bar', 2)]
>>> [(tag.name, hasattr(tag, 'counts')) for tag in Tag.objects.usage_for_queryset(Parrot.objects.filter(Q(perch__size__gt=6) | Q(state__startswith='l')))]
[(u'bar', False), (u'foo', False), (u'ter', False)]
>>> [(tag.name, tag.count) for tag in Tag.objects.usage_for_queryset(Parrot.objects.exclude(state='passed on'), counts=True)]
[(u'bar', 2), (u'foo', 2), (u'ter', 2)]
>>> [(tag.name, tag.count) for tag in Tag.objects.usage_for_queryset(Parrot.objects.exclude(state__startswith='p'), min_count=2)]
[(u'ter', 2)]
>>> [(tag.name, tag.count) for tag in Tag.objects.usage_for_queryset(Parrot.objects.exclude(Q(perch__size__gt=6) | Q(perch__smelly=False)), counts=True)]
[(u'foo', 1), (u'ter', 1)]
>>> [(tag.name, tag.count) for tag in Tag.objects.usage_for_queryset(Parrot.objects.exclude(perch__smelly=True).filter(state__startswith='l'), counts=True)]
[(u'bar', 1), (u'ter', 1)]
"""

try:
    from django.db.models.query import parse_lookup
except ImportError:
    __test__ = {'post-qsrf': tests_post_qsrf}
else:
    __test__ = {'pre-qsrf': tests_pre_qsrf}
