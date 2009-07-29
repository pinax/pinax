"""
This is pulled from
Eric Holscher's sandbox code at http://github.com/ericholscher/sandbox/blob/d32da8c36f257bb973a5c0b0fd8f9bca79062f11/serializers/yamlfk.py#L88
"""

from StringIO import StringIO

from django.db import models
from django.utils import simplejson
from django.core.serializers import base
from django.utils.encoding import smart_unicode
from django.core.serializers.python import _get_model
from django.core.serializers.json import Serializer as JSONSerializer


class Serializer(JSONSerializer):
    
    def handle_fk_field(self, obj, field):
        related = getattr(obj, field.name)
        if related is not None:
            unique_fields = get_unique_fields(related)
            if unique_fields:
                lookup_dict = {}
                for inner_field in unique_fields:
                    lookup_dict[inner_field.name] = getattr(related, inner_field.get_attname())
                related = lookup_dict
            elif field.rel.field_name == related._meta.pk.name:
                # Related to remote object via primary key
                related = related._get_pk_val()
            else:
                # Related to remote object via other field
                related = getattr(related, field.rel.field_name)

        if isinstance(related, dict):
            self._current[field.name] = related
        else:
            self._current[field.name] = smart_unicode(related, strings_only=True)


def Deserializer(stream_or_string, **options):
    """
    Deserialize a stream or string of JSON data.
    """
    if isinstance(stream_or_string, basestring):
        stream = StringIO(stream_or_string)
    else:
        stream = stream_or_string
    object_list = simplejson.load(stream)
 
    models.get_apps()
    for d in object_list:
        # Look up the model and starting build a dict of data for it.
        Model = _get_model(d["model"])
        data = {Model._meta.pk.attname : Model._meta.pk.to_python(d["pk"])}
        m2m_data = {}
 
        # Handle each field
        for (field_name, field_value) in d["fields"].iteritems():
            if isinstance(field_value, str):
                field_value = smart_unicode(field_value, options.get("encoding", settings.DEFAULT_CHARSET), strings_only=True)
 
            field = Model._meta.get_field(field_name)
 
            # Handle M2M relations
            if field.rel and isinstance(field.rel, models.ManyToManyRel):
                m2m_convert = field.rel.to._meta.pk.to_python
                m2m_data[field.name] = [m2m_convert(smart_unicode(pk)) for pk in field_value]
 
            # Handle FK fields
            elif field.rel and isinstance(field.rel, models.ManyToOneRel):
                if field_value is not None:
                    # handle a dictionary which means to lookup the instance
                    # and get the primary key this way (works great on
                    # GFK values)
                    if isinstance(field_value, dict):
                        lookup_params = {}
                        for k, v in field_value.iteritems():
                            lookup_params[k.encode("ascii")] = v
                        field_value = field.rel.to._default_manager.get(**lookup_params).pk
                    data[field.attname] = field.rel.to._meta.get_field(field.rel.field_name).to_python(field_value)
                else:
                    data[field.attname] = None
 
            # Handle all other fields
            else:
                data[field.name] = field.to_python(field_value)
 
        yield base.DeserializedObject(Model(**data), m2m_data)


def get_unique_fields(model):
    unique_fields = []
    for check in model._meta.unique_together:
        fields = [model._meta.get_field(f) for f in check]
        if len(fields) == len([f for f in fields if getattr(model, f.get_attname()) is not None]):
            unique_fields.extend(fields)
 
    # Gather a list of checks for fields declared as unique and add them to
    # the list of checks. Again, skip empty fields and any that did not validate.
    for f in model._meta.fields:
        if f.unique and getattr(model, f.get_attname()) is not None and not isinstance(f, models.AutoField):
            unique_fields.append(f)
 
    return unique_fields
