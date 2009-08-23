from datetime import datetime
from math import log

from django import template
from django.contrib.contenttypes.models import ContentType
from django.db import connection

from voting.models import Vote

register = template.Library()

def do_order_by_votes(parser, token):
    split = token.split_contents()
    if len(split) in (2, 3):
        return OrderByVotesNode(*split[1:])
    else:
        raise template.TemplateSyntaxError('%r tag takes one or two arguments.' % split[0])

class OrderByVotesNode(template.Node):
    def __init__(self, queryset_var, direction='desc'):
        self.queryset_var = template.Variable(queryset_var)
        self.direction = direction
    
    def render(self, context):
        key = self.queryset_var.var
        value = self.queryset_var.resolve(context)
        try:
            direction = template.Variable(self.direction).resolve(context)
        except template.VariableDoesNotExist:
            direction = 'desc'
        model = value.model
        qn = connection.ops.quote_name
        ctype = ContentType.objects.get_for_model(model)
        by_score = model.objects.extra(select={'score': """
                SELECT coalesce(SUM(vote), 0 )
                FROM %s
                WHERE content_type_id = %s
                AND object_id = %s.%s
            """ % (qn(Vote._meta.db_table), ctype.id, qn(model._meta.db_table), qn(model._meta.pk.attname))},
            order_by=[(direction == 'desc' and '-' or '') + 'score'])
        context[key] = by_score
        return u""

def do_order_by_reddit(parser, token):
    split = token.split_contents()
    if len(split) in (3, 4):
        return OrderByRedditNode(*split[1:])
    else:
        raise template.TemplateSyntaxError('%r tag takes one or two arguments.' % split[0])

class OrderByRedditNode(template.Node):
    def __init__(self, queryset_var, date_var, direction='desc'):
        self.queryset_var = template.Variable(queryset_var)
        self.date_var = date_var
        self.direction = direction

    def render(self, context):
        key = self.queryset_var.var
        values = self.queryset_var.resolve(context)
        votes = Vote.objects.get_scores_in_bulk(values)
        ratings = []
        for obj in values:
            age_timedelta = getattr(obj, self.date_var) - datetime(2005, 12, 8, 7, 46, 43)
            age = (age_timedelta.days * 86400) + age_timedelta.seconds
            try:
                obj_votes = votes[obj.id]['score']
            except KeyError:
                obj_votes = 0
            if obj_votes > 0:
                y = 1
            elif obj_votes < 0:
                y = -1
            else:
                y = 0
            z = max(abs(obj_votes), 1)
            
            rating = log(z, 10) + (y * age) / 45000.0
            ratings.append((rating, obj))
        ratings.sort(cmp=lambda x, y: cmp(y[0], x[0]))
        by_score = [x[1] for x in ratings]
        try:
            direction = template.Variable(self.direction).resolve(context)
        except template.VariableDoesNotExist:
            direction = 'desc'
        if direction == 'asc':
            by_score.reverse()
        context[key] = by_score
        return u""


register.tag('order_by_votes', do_order_by_votes)
register.tag('order_by_reddit', do_order_by_reddit)
