from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from dbtemplates.models import Template

class TemplateAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('name', 'content', 'sites')}),
        (_('Date information'), {
            'fields': ('creation_date', 'last_changed'),
            'classes': ('collapse',)
        }),
    )
    list_display = ('name', 'creation_date', 'last_changed')
    search_fields = ('name', 'content')

admin.site.register(Template, TemplateAdmin)
