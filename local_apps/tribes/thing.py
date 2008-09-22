import things
from django.db import connection

class TribeThing(things.ModelThing):
    created = things.OrderField(verbose_name_asc='Oldest', 
        verbose_name_desc='Newest', url_asc='oldest', url_desc='newest', 
        field_url='date')
    name = things.OrderField()
    members = things.OrderCountField(
        verbose_name_asc='Least Members', 
        verbose_name_desc='Most Members', 
        url_asc='last-members', 
        url_desc='most-members', 
        field_url='members'
    )
    topics = things.OrderCountField(
        verbose_name_asc='Least Topics', 
        verbose_name_desc='Most Topics', 
        url_asc='least-topics', 
        url_desc='most-topics', 
        field_url='topics'
    )
    search = ('name', 'description')
    template_dir = 'tribes'
    list_template_name = 'tribes.html'