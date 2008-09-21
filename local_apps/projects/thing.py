import things
from django.db import connection

class ProjectThing(things.ModelThing):
    created = things.OrderField(verbose_name_asc='Oldest', 
        verbose_name_desc='Newest', url_asc='oldest', url_desc='newest', 
        field_url='date')
    name = things.OrderField()
    member_count = things.OrderField(verbose_name_asc='Smallest', 
        verbose_name_desc='Largest', url_asc='smallest', url_desc='largest',
        field_url='size')
    search = ('name', 'description')
    template_dir = 'projects'
    list_template_name = 'projects.html'
    
    def get_query_set(self, m2m_name='member_users'):
        m2m_field = self.model._meta.get_field(m2m_name)
        qn = connection.ops.quote_name
        SQL = """
        SELECT COUNT(*) 
        FROM %(m2m_table)s 
        WHERE %(m2m_table)s.%(column_name)s = %(self_table)s.id
        """ % {
            'm2m_table': qn(m2m_field.m2m_db_table()),
            'column_name': qn(m2m_field.m2m_column_name()),
            'self_table': qn(self.model._meta.db_table),
        }
        return self.model._default_manager.extra(select={'member_count': SQL})