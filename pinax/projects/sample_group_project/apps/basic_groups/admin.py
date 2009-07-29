from django.contrib import admin
from basic_groups.models import BasicGroup

class BasicGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'creator', 'created')

admin.site.register(BasicGroup, BasicGroupAdmin)
