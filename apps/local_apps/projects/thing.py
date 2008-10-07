import things
from django.db import connection

class ProjectThing(things.Thing):
    created = things.OrderField(
        verbose_name_asc='Age', 
        verbose_name_desc='Age', 
        url_asc='oldest', 
        url_desc='newest', 
        field_url='date',
        reverse=True
    )
    name = things.OrderField(
        verbose_name_asc='Name', 
        verbose_name_desc='Name'
    )
    member_users = things.OrderCountField(
        verbose_name_asc='Member Count', 
        verbose_name_desc='Member Count', 
        url_asc='least-members', 
        url_desc='most-members', 
        field_url='members'
    )
    topics = things.OrderCountField(
        verbose_name_asc='Topic Count', 
        verbose_name_desc='Topic Count', 
        url_asc='least-topics', 
        url_desc='most-topics', 
        field_url='topics'
    )
    search = ('name', 'description')
    template_dir = 'projects'
    list_template_name = 'projects.html'