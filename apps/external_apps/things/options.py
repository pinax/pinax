import copy
from operator import or_
from django.conf.urls.defaults import *
from django.http import HttpResponse, Http404
from django.template import RequestContext
from django.template.loader import select_template
from django.core.urlresolvers import reverse
from django.db.models import Q
from things.fields import BaseField, AggregateBase, DESCENDING

__all__ = ('Thing', 'ModelThing', 'ThingGroup')

class MultipleDefaultOrderFields(Exception):
    pass

class BaseThingMetaclass(type):
    def __new__(cls, name, bases, attrs):
        fields = {}
        for k, v in attrs.iteritems():
            if isinstance(v, BaseField):
                fields[k] = v
        attrs['fields'] = fields
        new_class = super(BaseThingMetaclass, cls).__new__(cls, name, bases, 
            attrs)
        return new_class

class Thing(object):
    __metaclass__ = BaseThingMetaclass
    
    fields = {}
    detail_template_name = None
    list_template_name = None
    template_dir = 'things'
    search = []
    
    def __init__(self, qs):
        self.qs = qs
        self.model = qs.model
        self.opts = self.model._meta
        self.default_order_field = None
        fields = copy.deepcopy(self.fields)
        for (name, field) in fields.iteritems():
            assert isinstance(field, BaseField) == True
            field.parent = self
            field.field_name = name
            if getattr(field, 'default_order_field', None) is not None:
                if self.default_order_field is None:
                    self.default_order_field = field
                else:
                    raise MultipleDefaultOrderFields([self.default_order_field,
                        field])
        self.fields = fields
        if not self.detail_template_name:
            self.detail_template_name = '%s_detail.html' % self.opts.module_name
        if not self.list_template_name:
            self.list_template_name = '%s_list.html' % self.opts.module_name
    
    def list_view(self, request, descending=False, field=None, 
        template_object_name='objects', template_name=None, 
        extra_context = {}, templates=[], **kwargs):
        if template_name is None:
            template_name = self.list_template_name
        items = self.get_query_set()
        terms = request.REQUEST.get('search', '')
        if terms and bool(self.search):
            kwargs = {}
            if isinstance(self.search, basestring):
                items = items.filter(**{"%s__icontains" % self.search: terms})
            else:
                q_list = [Q(**{'%s__icontains' % s: terms}) for s in self.search]
                items = items.filter(reduce(or_, q_list))
        if field is None:
            field = self.default_order_field
            descending = getattr(field, 'default_order_field', None) == DESCENDING
        if field is not None:
            reverse = descending ^ field.reverse
            pre = ''
            if reverse:
                pre = '-'
            if field.custom_aggregate_function is not None:
                caf = field.custom_aggregate_function
                vgetter = lambda val: val[1]
                items = [i[0] for i in sorted([(j, caf(request, j)) for j in items], 
                    key=vgetter, reverse=reverse)]
            elif field.custom_aggregate_dict_function is not None:
                pk_sort_dict = field.custom_aggregate_dict_function(request)
                items = list(items.filter(pk__in=pk_sort_dict.keys()))
                items.sort(key=lambda val: pk_sort_dict[val.id], reverse=reverse)
            elif isinstance(field, AggregateBase):
                items = items.order_by('%s%s' % (pre, field.get_aggregate_name()))
            else:
                items = items.order_by('%s%s' % (pre, field.field_name))
        if not templates:
            templates = ['%s/%s' % (self.template_dir, template_name,),
                '%s/list.html' % self.template_dir, 'things/list.html']
        context = {
            template_object_name: items, 
            'fields': self.fields.values(), 
            'field': field,
            'descending': descending,
            'url_prefix': self.url_prefix,
            'name_prefix': self.name_prefix,
            'search_enabled': bool(self.search),
            'terms': terms,
        }
        context.update(extra_context)
        t = select_template(templates)
        c = RequestContext(request, context)
        return HttpResponse(t.render(c))
    
    def detail_view(self, request, pk, template_object_name='object', 
        template_name=None, url_prefix=None, extra_context={}):
        if template_name is None:
            template_name = self.detail_template_name
        try:
            obj = self.get_query_set().get(pk=pk)
        except self.model.DoesNotExist:
            raise Http404
        list_url = reverse('%s_list' % (self.name_prefix,), kwargs={
            'url_prefix': self.url_prefix,
        })
        templates = ['%s/%s' % (self.template_dir, template_name,),
            '%s/detail.html' % self.template_dir, 'things/detail.html']
        context = {
            template_object_name: obj,
            'list_url': list_url,
        }
        context.update(extra_context)
        t = select_template(templates)
        c = RequestContext(request, context)
        return HttpResponse(t.render(c))
    
    def urls(self, prefix='^', name_prefix='things', url_prefix='',
        extra_context={}):
        self.name_prefix = name_prefix # Is this robust enough? Needs testing.
        self.url_prefix = url_prefix
        if self.url_prefix is None:
            self.url_prefix = "%s/%s/" % (self.opts.app_label, 
                self.opts.module_name)
        tmp_urls = [
            url(r'%s(?P<url_prefix>%s)$' % (prefix, self.url_prefix),
                self.list_view, 
                {'extra_context': extra_context}, 
                name='%s_list' % name_prefix),
            url(r'%s(?P<url_prefix>%s)detail/(?P<pk>\d+)/$' % (prefix, 
                self.url_prefix), 
                self.detail_view,
                {'extra_context': extra_context},
                name='%s_detail' % name_prefix)
        ]
        tmp_urls.extend([
            url('%s(?P<url_prefix>%s)order/%s/%s/' % (prefix, self.url_prefix,
                field.field_url, field.url_asc), 
                self.list_view, 
                {
                    'descending': False, 
                    'field': self.fields.get(field.field_name, None),
                    'extra_context': extra_context,
                }, 
                name='%s_%s_list_asc' % (name_prefix, field.field_url))
            for (name, field) in self.fields.iteritems()
        ])
        tmp_urls.extend([
            url('%s(?P<url_prefix>%s)order/%s/%s/' % (prefix, self.url_prefix, 
            field.field_url, field.url_desc), 
                self.list_view, 
                {
                    'descending': True, 
                    'field': self.fields.get(field.field_name, None),
                    'extra_context': extra_context,
                }, 
                name='%s_%s_list_desc' % (name_prefix, field.field_url))
            for (name, field) in self.fields.iteritems()
        ])
        return patterns('', *tmp_urls)
    
    def get_query_set(self):
        query_set = self.qs
        for field_name, field in self.fields.iteritems():
            if isinstance(field, AggregateBase):
                query_set = field.modify_query_set(query_set)
        return query_set

class ModelThing(Thing):
    def __init__(self, model):
        qs = model._default_manager.all()
        super(ModelThing, self).__init__(qs)

class GroupDict(dict):
    def __init__(self, parent, *args, **kwargs):
        self.parent = parent
        super(GroupDict, self).__init__(*args, **kwargs)
        
    def url(self):
        return reverse(
            '%s_%s_list' % (self.parent.name_prefix, self['url_name']), 
            kwargs={'url_prefix': '%s/' % self['url_name']}
        )

class ThingGroup(object):
    """
    [
        {
            'queryset': MyModel.objects.filter(name='asdf'),
            'name': 'my_name',
            'url_name': 'my_url_name',
            'description': 'my_description',
        },
    ]
    """
    template_name = None
    template_dir = 'things'
    
    def __init__(self, thing, group_dicts=None, group_func=None):
        if group_dicts is not None and group_func is not None:
            raise TypeError("Both group_dicts and group_func cannot be specified.")
        if not group_dicts and not group_func:
            raise TypeError("Either group_dicts or group_func must be specified.")
        if group_dicts:
            groups = group_dicts
        else:
            groups = group_func(thing)
            
        self.groups = []
        for group in groups:
            for key in ('queryset', 'name', 'url_name'):
                if key not in group:
                    raise TypeError("Group dictionary must include a '%s' argument." % key)
            self.groups.append(GroupDict(self, group))

        self.thing = thing

    def urls(self, prefix='^', name_prefix='things', url_prefix='',
        extra_context={}):
        self.name_prefix = name_prefix # Is this robust enough? Needs testing.
        self.prefix = prefix
        self.url_prefix = url_prefix
        tmp_urls = [
            url(
                r'%s(?P<url_prefix>%s)$' % (prefix, self.url_prefix),
                self.group_view,
                {'extra_context': extra_context},
                name='%s_group_list' % name_prefix),
        ]
        for group in self.groups:
            thing = self.thing(qs=group['queryset'])
            description = group.get('description', '')
            context = {
                'group_name': group['name'],
                'group_description': description,
                'groups': self.groups,
            }
            context.update(extra_context)
            tmp_urls.extend(thing.urls(
                prefix='%s%s' % (prefix, self.url_prefix),
                extra_context=context,
                name_prefix='%s_%s' % (name_prefix, group['url_name']),
                url_prefix='%s/' % group['url_name'],
            ))
        return patterns('', *tmp_urls)
    
    def group_view(self, request, extra_context={}, url_prefix=None):
        context = {
            'groups': self.groups,
        }
        context.update(extra_context)
        if self.template_name is None:
            template_name = '%s_groups.html' % (self.__class__.__name__,)
        else:
            template_name = self.template_name
        templates = ['%s/%s' % (self.template_dir, template_name,),
            '%s/groups.html' % self.template_dir, 'things/groups.html']
        t = select_template(templates)
        c = RequestContext(request, context)
        return HttpResponse(t.render(c))