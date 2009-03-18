from django.contrib import admin
from tribes.models import Tribe, Topic

class TribeAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'creator', 'created', 'deleted')  

class TopicAdmin(admin.ModelAdmin):
    list_display = ('title', )

admin.site.register(Tribe, TribeAdmin)
admin.site.register(Topic, TopicAdmin)
