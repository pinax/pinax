
from django.contrib import admin

from announcements.models import Announcement
from announcements.forms import AnnouncementAdminForm

class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("title", "creator", "creation_date", "members_only")
    list_filter = ("members_only",)
    form = AnnouncementAdminForm

admin.site.register(Announcement, AnnouncementAdmin)
