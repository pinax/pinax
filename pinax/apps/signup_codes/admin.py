
from django.contrib import admin

from signup_codes.models import SignupCode


class SignupCodeAdmin(admin.ModelAdmin):
    list_display = ("code", "max_uses", "use_count", "expiry", "created")
    list_filter = ("created",)

admin.site.register(SignupCode, SignupCodeAdmin)
