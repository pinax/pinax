from django.contrib import admin

from pinax.apps.account.models import Account, PasswordReset


class PasswordResetAdmin(admin.ModelAdmin):
    list_display = ["user", "temp_key", "timestamp", "reset"]


admin.site.register(Account)
admin.site.register(PasswordReset, PasswordResetAdmin)