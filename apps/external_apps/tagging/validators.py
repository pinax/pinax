"""
Oldforms validators for tagging related fields - these are still
required for basic ``django.contrib.admin`` application field validation
until the ``newforms-admin`` branch lands in trunk.
"""
from django import forms
from django.utils.translation import ugettext as _

from tagging import settings
from tagging.utils import parse_tag_input

def is_tag_list(value):
    """
    Validates that ``value`` is a valid list of tags.
    """
    for tag_name in parse_tag_input(value):
        if len(tag_name) > settings.MAX_TAG_LENGTH:
            raise forms.ValidationError(
                _('Each tag may be no more than %s characters long.') % settings.MAX_TAG_LENGTH)
    return value

def is_tag(value):
    """
    Validates that ``value`` is a valid tag.
    """
    tag_names = parse_tag_input(value)
    if len(tag_names) > 1:
        raise ValidationError(_('Multiple tags were given.'))
    elif len(tag_names[0]) > settings.MAX_TAG_LENGTH:
        raise forms.ValidationError(
            _('A tag may be no more than %s characters long.') % settings.MAX_TAG_LENGTH)
    return value
