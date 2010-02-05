from django.contrib import admin
from attachments.admin import AttachmentInlines
from pinax.apps.tasks.models import Task



class TaskOptions(admin.ModelAdmin):
    inlines = [AttachmentInlines]



admin.site.register(Task, TaskOptions)