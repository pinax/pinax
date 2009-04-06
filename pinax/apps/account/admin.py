from django.contrib import admin
from account.models import Account, OtherServiceInfo, PasswordReset

admin.site.register(Account)
admin.site.register(OtherServiceInfo)

class PasswordResetAdmin(admin.ModelAdmin):
    list_display = ('user', 'temp_key', 'timestamp', 'reset')

admin.site.register(PasswordReset, PasswordResetAdmin)