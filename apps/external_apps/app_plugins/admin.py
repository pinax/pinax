from django.contrib import admin
from app_plugins.models import PluginPoint, Plugin, UserPluginPreference
from app_plugins.forms import AdminPluginPointForm, AdminPluginForm

class PluginPointAdmin(admin.ModelAdmin):
    list_display = ('label', 'index', 'registered', 'status')
    list_filter = ('registered', 'status')
    form = AdminPluginPointForm

class PluginAdmin(admin.ModelAdmin):
    list_display = ('label', 'index', 'registered', 'required', 'status')
    list_filter = ('registered', 'status')
    form = AdminPluginForm

class UserPluginPreferenceAdmin(admin.ModelAdmin):
    list_display = ('plugin', 'user', 'index', 'visible')
    list_filter = ('visible',)

admin.site.register(PluginPoint, PluginPointAdmin)
admin.site.register(Plugin, PluginAdmin)
admin.site.register(UserPluginPreference, UserPluginPreferenceAdmin)

