from django import forms
from django.http import HttpResponse
from django.views.decorators.http import require_POST

from ajax_validation.utils import LazyEncoder

def validate(request, *args, **kwargs):
    form_class = kwargs.pop('form_class')
    extra_args_func = kwargs.pop('callback', lambda request, *args, **kwargs: {})
    kwargs = extra_args_func(request, *args, **kwargs)
    kwargs['data'] = request.POST
    form = form_class(**kwargs)
    if form.is_valid():
        data = {
            'valid': True,
        }
    else:
        if request.POST.getlist('fields'):
            fields = request.POST.getlist('fields') + ['__all__']
            errors = dict([(key, val) for key, val in form.errors.iteritems() if key in fields])
        else:
            errors = form.errors
        final_errors = {}
        for key, val in errors.iteritems():
            if not isinstance(form.fields[key], forms.FileField):
                html_id = form.fields[key].widget.attrs.get('id') or form[key].auto_id
                html_id = form.fields[key].widget.id_for_label(html_id)
                final_errors[html_id] = val
        data = {
            'valid': False,
            'errors': final_errors,
        }
    json_serializer = LazyEncoder()
    return HttpResponse(json_serializer.encode(data), mimetype='application/json')
validate = require_POST(validate)
