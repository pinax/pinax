from datetime import datetime
from math import log

from django import template
from django.contrib.contenttypes.models import ContentType
from django.db import connection

from voting.models import Vote

register = template.Library()

def do_order_by_votes(parser, token):
    split = token.split_contents()
    if len(split) == 2:
        return OrderByVotesNode(split[1])
    else:
        raise template.TemplateSyntaxError('%r tag takes one argument.' % split[0])

class OrderByVotesNode(template.Node):
    def __init__(self, queryset_var):
        self.queryset_var = template.Variable(queryset_var)
    
    def render(self, context):
        key = self.queryset_var.var
        value = self.queryset_var.resolve(context)
        model = value.model
        
        qn = connection.ops.quote_name
        ctype = ContentType.objects.get_for_model(model)
        by_score = model.objects.extra(select={'score': """
                SELECT coalesce(SUM(vote), 0 ) 
                FROM %s
                WHERE content_type_id = %s
                AND object_id = %s."id"
            """ % (qn(Vote._meta.db_table), ctype.id, qn(model._meta.db_table))},
            order_by=['-score'])
        context[key] = by_score
        return u""

def do_order_by_reddit(parser, token):
    split = token.split_contents()
    if len(split) == 3:
        return OrderByRedditNode(*split[1:])
    else:
        raise template.TemplateSyntaxError('%r tag takes one argument.' % split[0])

class OrderByRedditNode(template.Node):
    def __init__(self, queryset_var, date_var):
        self.queryset_var = template.Variable(queryset_var)
        self.date_var = date_var
    
    def render(self, context):
        key = self.queryset_var.var
        values = self.queryset_var.resolve(context)
        votes = Vote.objects.get_scores_in_bulk(values)
        ratings = []
        for obj in values:
            age = (getattr(obj, self.date_var) - datetime(2005, 12, 8, 7, 46, 43)).seconds
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
        
        
        context[key] = by_score
        return u""


register.tag('order_by_votes', do_order_by_votes)
register.tag('order_by_reddit', do_order_by_reddit)
