from django.contrib import admin
from newprojects.models import Project

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'creator', 'created')

admin.site.register(Project, ProjectAdmin)
