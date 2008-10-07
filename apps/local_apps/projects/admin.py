from django.contrib import admin
from projects.models import Project, Topic, Task

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'creator', 'created', 'private', 'deleted')

class TopicAdmin(admin.ModelAdmin):
    list_display = ('title', )

admin.site.register(Project, ProjectAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Task)

