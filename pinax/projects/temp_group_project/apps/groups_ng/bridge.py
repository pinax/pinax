from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render_to_response

class ContentBridge(object):
    def __init__(self, group_model, content_app_name):
        self.group_model = group_model
        self.content_app_name = content_app_name
    
    def render(self, template_name, context, context_instance=None):
        ctype = ContentType.objects.get_for_model(self.group_model)
        print [
            '%s/%s/%s' % (ctype.app_label, self.content_app_name, template_name),
            '%s/%s' % (self.content_app_name, template_name),
        ]
        return render_to_response([
            '%s/%s/%s' % (ctype.app_label, self.content_app_name, template_name),
            '%s/%s' % (self.content_app_name, template_name),
        ], context, context_instance=context_instance)
    
    def get_group(self, slug):
        return self.group_model._default_manager.get(slug=slug)