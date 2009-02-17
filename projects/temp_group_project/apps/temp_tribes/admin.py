from django.contrib import admin
from temp_tribes.models import Tribe

class TribeAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'creator', 'created', 'deleted')  

admin.site.register(Tribe, TribeAdmin)
