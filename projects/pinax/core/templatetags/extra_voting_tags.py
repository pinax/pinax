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
            """ %     (qn(Vote._meta.db_table),
                               ctype.id, qn(model._meta.db_table))},
            order_by=['-score'])
        context[key] = by_score
        return u""
        
        
        #ctype = ContentType.objects.get_for_model(value.model)
        #query = """
        #SELECT
        #    %(table)s, SUM(vote) AS score
        #FROM
        #    votes, (%(subquery)s) AS foo
        #WHERE
        #    content_type_id = %(ctype_id)s AND object_id = %(table)s
        #GROUP BY
        #    %(table)s
        #ORDER BY
        #    score DESC;""" % {
        #        "table": value.model._meta.db_table,
        #        "subquery": value.query,
        #        "ctype_id": ctype.id,
        #    }
        #    
        #cursor = connection.cursor()
        #cursor.execute(query)
        #results = cursor.fetchall()
        #
        #objects = value.model.objects.in_bulk([id for id, score in results])
        #def r():
        #    for id, score in results:
        #        if id in objects:
        #            yield objects[id]
        #context[key] = r()
        #return u""

register.tag('order_by_votes', do_order_by_votes)