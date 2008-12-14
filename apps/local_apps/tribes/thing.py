import things
from django.db import connection
from django.utils.translation import ugettext_lazy as _

class TribeThing(things.Thing):
    created = things.OrderField(
        verbose_name_asc=_('Age'), 
        verbose_name_desc=_('Age'), 
        url_asc='oldest', 
        url_desc='newest', 
        field_url='date',
        reverse=True
    )
    name = things.OrderField(
        verbose_name_asc=_('Name'), 
        verbose_name_desc=_('Name')
    )
    members = things.OrderCountField(
        verbose_name_asc=_('Member Count'), 
        verbose_name_desc=_('Member Count'), 
        url_asc='least-members', 
        url_desc='most-members', 
        field_url='members'
    )
    topics = things.OrderCountField(
        verbose_name_asc=_('Topic Count'), 
        verbose_name_desc=_('Topic Count'), 
        url_asc='least-topics', 
        url_desc='most-topics', 
        field_url='topics'
    )
    search = ('name', 'description')
    template_dir = 'tribes'
    list_template_name = 'tribes.html'