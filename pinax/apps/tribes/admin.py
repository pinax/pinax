from django.contrib import admin
from tribes.models import Tribe

class TribeAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'creator', 'created')

admin.site.register(Tribe, TribeAdmin)
