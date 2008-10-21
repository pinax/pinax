import things
from django.conf.urls.defaults import *
from django.db.models.base import ModelBase
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext

class AlreadyRegistered(Exception):
    pass

class NotRegistered(Exception):
    pass

class ThingSite(object):
    def __init__(self, name_prefix="things"):
        self._registry = {}
        self.name_prefix = name_prefix
    
    def register(self, model_or_iterable, thing_class=None, **options):
        """
        Registers the given model(s) with the given thing class.  The model(s)
        should be Model classes, not instances.
        
        If a thing class isn't given, it will use ThingAdmin (the default
        thing options). 
        
        If a model is already registered, this will raise 
        AlreadyRegistered.
        """
        #thing_class = thing_class or ThingAdmin
        if isinstance(model_or_iterable, ModelBase):
            model_or_iterable = (model_or_iterable,)
        for model in model_or_iterable:
            if model in self._registry:
                raise AlreadyRegistered('The model %s is already registered' % model.__name__)
            if not thing_class:
                thing = things.ModelThing(model)
                thing.fields = {}
                for field in model._meta.fields:
                    of = things.OrderField()
                    of.parent = thing
                    of.field_name = field.attname
                    thing.fields[field.attname] = of
            else:
                thing = thing_class(model)
            self._registry[model] = thing
    
    def unregister(self, model_or_iterable):
        """
        Unregisters the given model(s).
        
        If a model isn't already registered, this will raise NotRegistered.
        """
        if isinstance(model_or_iterable, ModelBase):
            model_or_iterable = (model_or_iterable,)
        for model in model_or_iterable:
            if model not in self._registry:
                raise NotRegistered('The model %s is not registered' % model.__name__)
            del self._registry[model]
    
    def urls(self, prefix='^things/'):
        urlpatterns = patterns('', 
            url(r'%s$' % (prefix,), self.index, name="%s_index" % self.name_prefix)
        )
        for (model, model_thing) in self._registry.iteritems():
            urlpatterns += model_thing.urls(prefix, self.name_prefix)
        return urlpatterns
    
    def index(self, request):
        models = [{ 'model': m,
                    'model_thing': self._registry[m],
                    'url': reverse('%s_list' % self.name_prefix, kwargs={
                        'url_prefix': self._registry[m].url_prefix,
                     }) } for m in self._registry.iterkeys()]
        context = {
            'models': models,
            'thing_site': self,
        }
        return render_to_response('things/index.html', context, context_instance=RequestContext(request))

site = ThingSite()