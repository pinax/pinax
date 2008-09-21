import things

class ProjectThing(things.ModelThing):
    created = things.OrderField(verbose_name_asc='Oldest', 
        verbose_name_desc='Newest', url_asc='oldest', url_desc='newest', 
        field_url='date')
    name = things.OrderField()
    member_users = things.OrderField(verbose_name_asc='Largest', 
        verbose_name_desc='Smallest', url_asc='largest', url_desc='smallest',
        field_url='size')
    search = ('name', 'description')
    template_dir = 'projects'
    list_template_name = 'projects.html'