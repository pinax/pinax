import sys

from django.shortcuts import render_to_response
from django.conf.urls.defaults import patterns, url as urlpattern
from django.core.urlresolvers import RegexURLPattern, RegexURLResolver, reverse as dreverse

from django.contrib.contenttypes.models import ContentType


class ContentBridge(object):
    def __init__(self, group_model, content_app_name):
        self.group_model = group_model
        self.content_app_name = content_app_name
        
        # attach the bridge to the model itself. we need to access it when
        # using groupurl to get the correct prefix for URLs for the given
        # group.
        self.group_model.content_bridge = self
    
    def include_urls(self, module_name, url_prefix, kwargs=None):
        if kwargs is None:
            kwargs = {}
        
        prefix = self.content_app_name
        
        __import__(module_name)
        module = sys.modules[module_name]
        urls = module.urlpatterns

        final_urls = []

        for url in urls:
            extra_kwargs = {"bridge": self}
            
            if isinstance(url, RegexURLPattern):
                regex = url_prefix + url.regex.pattern.lstrip("^")
                callback = url._callback or url._callback_str
                name = prefix + "_" + (url.name or "")
                extra_kwargs.update(kwargs)
                extra_kwargs.update(url.default_args)
                final_urls.append(urlpattern(regex, callback, extra_kwargs, name))
            else:
                # i don't see this case happening much at all. this case will be
                # executed likely if url is a RegexURLResolver. nesting an include
                # at the content object level may not be supported, but maybe the
                # code below works. i don't have time to test it, but if you are
                # reading this because something is broken then give it a shot.
                # then report back :-)
                raise Exception("ContentBridge.include_urls does not support a nested include.")

                # regex = url_prefix + url.regex.pattern.lstrip("^")
                # urlconf_name = url.urlconf_name
                # extra_kwargs.update(kwargs)
                # extra_kwargs.update(url.default_kwargs)
                # final_urls.append(urlpattern(regex, [urlconf_name], extra_kwargs))

        return patterns("", *final_urls)
    
    def reverse(self, view_name, group, kwargs=None):
        if kwargs is None:
            kwargs = {}
        
        prefix = self.content_app_name
        final_kwargs = {}
        
        final_kwargs.update(group.get_url_kwargs())
        final_kwargs.update(kwargs)
        
        return dreverse("%s_%s" % (prefix, view_name), kwargs=final_kwargs)
    
    def render(self, template_name, context, context_instance=None):
        ctype = ContentType.objects.get_for_model(self.group_model)
        return render_to_response([
            '%s/%s/%s' % (ctype.app_label, self.content_app_name, template_name),
            '%s/%s' % (self.content_app_name, template_name),
        ], context, context_instance=context_instance)
    
    def group_base_template(self, template_name="content_base.html"):
        return "%s/%s" % (self.content_app_name, template_name)
    
    def get_group(self, slug):
        return self.group_model._default_manager.get(slug=slug)
        