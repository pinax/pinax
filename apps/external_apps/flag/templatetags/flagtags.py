from django import template

from django.contrib.contenttypes.models import ContentType

register = template.Library()

def flag(context, content_object, creator_field):
    content_type = ContentType.objects.get(app_label=content_object._meta.app_label, model=content_object._meta.module_name)
    return {
        'content_type': content_type.id,
        'object_id': content_object.id,
        'creator_field': creator_field,
        'request': context['request'],
        'user': context['user'],
    }


register.inclusion_tag('flag/flag_form.html', takes_context=True)(flag)
