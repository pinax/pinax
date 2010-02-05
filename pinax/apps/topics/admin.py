from django.contrib import admin

from pinax.apps.topics.models import Topic



class TopicAdmin(admin.ModelAdmin):
    list_display = ["title"]



admin.site.register(Topic, TopicAdmin)