from django.contrib import admin

from pinax.apps.waitinglist.models import WaitingListEntry


class WaitingListEntryAdmin(admin.ModelAdmin):
    list_display = ["email", "created"]
    search_fields = ["email"]


admin.site.register(WaitingListEntry, WaitingListEntryAdmin)