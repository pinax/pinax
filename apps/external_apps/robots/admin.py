from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from robots.models import Url, Rule
from robots.forms import RuleAdminForm

class RuleAdmin(admin.ModelAdmin):
    form = RuleAdminForm
    fieldsets = (
        (None, {'fields': ('robot', 'sites')}),
        (_('URL patterns'), {'fields': ('allowed', 'disallowed')}),
        (_('Advanced options'), {'classes': ('collapse',), 'fields': ('crawl_delay',)}),
    )
    list_filter = ('sites',)
    list_display = ('robot', 'allowed_urls', 'disallowed_urls')
    search_fields = ('robot','urls')

admin.site.register(Url)
admin.site.register(Rule, RuleAdmin)
