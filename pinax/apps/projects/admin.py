from django.contrib import admin
from projects.models import Project, Topic, Task, ProjectMember

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'creator', 'created', 'private', 'deleted')

class TopicAdmin(admin.ModelAdmin):
    list_display = ('title', )
    
class ProjectMemberAdmin(admin.ModelAdmin):
   list_display = ('user', 'project', 'away', 'away_message', 'away_since')

admin.site.register(Project, ProjectAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Task)
admin.site.register(ProjectMember, ProjectMemberAdmin) 
