from django.http import HttpResponse, Http404
from django.db.models import get_model
from django.utils import simplejson
from tagging.models import Tag
from django.contrib.contenttypes.models import ContentType

def autocomplete(request, app_label, model):
    try:
        model = ContentType.objects.get(app_label=app_label, model=model)
    except:
        raise Http404
    
    if not request.GET.has_key('q'):
        raise Http404
    else:
        q = request.GET['q']

    limit = request.GET.get('limit', None)
    
    tags = Tag.objects.filter(items__content_type=model, name__istartswith=q).distinct().order_by('name')[:limit]
    tag_list = '\n'.join([tag.name for tag in tags if tag])
    
    return HttpResponse(tag_list)
