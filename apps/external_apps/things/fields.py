from django.template import defaultfilters
from django.core.urlresolvers import reverse
from django.db.models.options import FieldDoesNotExist
from django.db import connection
from django.contrib.contenttypes.models import ContentType

__all__ = ('OrderField', 'ForeignKeyAggregate', 'GenericForeignKeyAggregate',
    'OrderSumField', 'OrderCountField', 'OrderGenericCountField',
    'OrderGenericSumField', 'ASCENDING', 'DESCENDING')

ASCENDING = 1
DESCENDING = 2

qn = connection.ops.quote_name

def create_setter(prop):
    def inner(self, value):
        setattr(self, prop, value)
    return inner

class BaseField(object):
    parent = None
    field_name = None

class OrderField(BaseField):
    def __init__(self, verbose_name_asc=None, verbose_name_desc=None, 
                 url_asc=None, url_desc=None, field_url=None, 
                 custom_aggregate_function=None, default_sort_descending=True,
                 reverse=False, custom_aggregate_dict_function=None,
                 default_order_field=None):
        self._verbose_name_asc = verbose_name_asc
        self._verbose_name_desc = verbose_name_desc
        self._url_asc = url_asc
        self._url_desc = url_desc
        self._field_url = field_url
        self.reverse = reverse
        self.default_sort_descending = default_sort_descending
        self.custom_aggregate_function = custom_aggregate_function
        self.custom_aggregate_dict_function = custom_aggregate_dict_function
        self.default_order_field = default_order_field
    
    def _get_verbose_name_asc(self):
        if self._verbose_name_asc:
            return self._verbose_name_asc
        else:
            return u'%s Ascending' % defaultfilters.capfirst(self.field_name)
    verbose_name_asc = property(_get_verbose_name_asc, create_setter('_verbose_name_asc'))
    
    def _get_verbose_name_desc(self):
        if self._verbose_name_asc:
            return self._verbose_name_desc
        else:
            return u'%s Descending' % defaultfilters.capfirst(self.field_name)
    verbose_name_desc = property(_get_verbose_name_desc, create_setter('_verbose_name_desc'))
    
    def _get_url_asc(self):
        if self._url_asc:
            return self._url_asc
        else:
            return 'ascending'
    url_asc = property(_get_url_asc, create_setter('_url_asc'))
    
    def _get_url_desc(self):
        if self._url_desc:
            return self._url_desc
        else:
            return 'descending'
    url_desc = property(_get_url_desc, create_setter('_url_desc'))

    def _get_field_url(self):
        if self._field_url:
            return self._field_url
        else:
            return self.field_name
    field_url = property(_get_field_url, create_setter('_field_url'))

    def full_url_asc(self):
        return reverse('%s_%s_list_asc' % (
            self.parent.name_prefix, self.field_url), 
            kwargs={
                'url_prefix': self.parent.url_prefix,
        })
        
    def full_url_desc(self):
        return reverse('%s_%s_list_desc' % (
            self.parent.name_prefix, self.field_url),
            kwargs={
                'url_prefix': self.parent.url_prefix,
        })

class AggregateBase(BaseField):
    def get_aggregate_name(self):
        raise NotImplementedError
    
    def get_aggregate_sql(self):
        raise NotImplementedError
    
    def get_sql_args(self):
        raise NotImplementedError
    
    def modify_query_set(self, qs):
        sql = self.get_aggregate_sql()
        args = self.get_sql_args()
        return qs.extra(select={self.get_aggregate_name(): sql % args})

class ForeignKeyAggregate(AggregateBase):
    def get_sql_args(self):
        try:
            parent_field = self.parent.opts.get_field(self.field_name)
            m2m = True
        except FieldDoesNotExist:
            m2m = False
        self_table = qn(self.parent.opts.db_table)
        if m2m:
            related_table = qn(parent_field.m2m_db_table())
            related_column_name = qn(parent_field.m2m_column_name())
        else:
            # Need to instantiate the model, since we can't access RelatedManager
            # instances unless it's through an instance instead of a class.
            dummy_stupid = self.parent.model()
            related_manager = getattr(dummy_stupid, self.field_name)
            related_table = related_manager.model._meta.db_table
            children = related_manager.all().query.where.children
            related_column_name = None
            for child in children:
                if child[0] == related_table:
                    related_column_name = child[1]
                    break
            if related_column_name is None:
                raise ValueError("Could not determine relationship on related name %s" % self.field_name)
            related_table = qn(related_table)
            related_column_name = qn(related_column_name)
        return {
            'related_table': related_table,
            'related_column_name': related_column_name,
            'self_table': self_table,
        }

class GenericForeignKeyAggregate(AggregateBase):
    def get_sql_args(self):
        related_table = qn(self.generic_model._meta.db_table)
        self_content_type = int(ContentType.objects.get_for_model(
            self.parent.model).id)
        self_table = qn(self.parent.model._meta.db_table)
        return {
            'related_table': related_table,
            'self_content_type': self_content_type,
            'self_table': self_table,
        }

class OrderSumField(OrderField, ForeignKeyAggregate):
    def __init__(self, sum_field, *args, **kwargs):
        self.sum_field = sum_field
        super(OrderSumField, self).__init__(*args, **kwargs)
    
    def get_aggregate_sql(self):
        return """
            SELECT COALESCE(SUM(%(sum_field)s), 0)
            FROM %(related_table)s
            WHERE %(related_table)s.%(related_column_name)s = %(self_table)s.id
        """
    
    def get_aggregate_name(self):
        return '%s_sum' % self.field_name
    
    def get_sql_args(self):
        args = super(OrderSumField, self).get_sql_args().copy()
        args.update({'sum_field': self.sum_field})
        return args

class OrderCountField(OrderField, ForeignKeyAggregate):
    def get_aggregate_name(self):
        return '%s_count' % self.field_name
    
    def get_aggregate_sql(self):
        return """
        SELECT COUNT(*) 
        FROM %(related_table)s 
        WHERE %(related_table)s.%(related_column_name)s = %(self_table)s.id
        """

class OrderGenericCountField(OrderField, GenericForeignKeyAggregate):
    def __init__(self, generic_model, *args, **kwargs):
        self.generic_model = generic_model
        super(OrderGenericCountField, self).__init__(*args, **kwargs)

    def get_aggregate_name(self):
        return '%s_count' % self.field_name

    def get_aggregate_sql(self):
        return u"""
        SELECT COUNT(*)
        FROM %(related_table)s
        WHERE %(related_table)s.content_type_id=%(self_content_type)i
        AND %(related_table)s.object_id=%(self_table)s.id
        """
    
class OrderGenericSumField(OrderField, GenericForeignKeyAggregate):
    def __init__(self, generic_model, sum_field, *args, **kwargs):
        self.generic_model = generic_model
        self.sum_field = sum_field
        super(OrderGenericSumField, self).__init__(*args, **kwargs)

    def get_aggregate_name(self):
        return '%s_count' % self.field_name

    def get_sql_args(self):
        args = super(OrderGenericSumField, self).get_sql_args().copy()
        args.update({'sum_field': self.sum_field})
        return args

    def get_aggregate_sql(self):
        return u"""
        SELECT COALESCE(SUM(%(sum_field)s), 0)
        FROM %(related_table)s
        WHERE %(related_table)s.content_type_id=%(self_content_type)i
        AND %(related_table)s.object_id=%(self_table)s.id
        """