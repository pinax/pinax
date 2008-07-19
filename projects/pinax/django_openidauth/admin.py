from django.contrib import admin
from django_openidauth.models import UserOpenID

class UserOpenIDAdmin(admin.ModelAdmin):
    raw_id_fields = ('user',) 

admin.site.register(UserOpenID, UserOpenIDAdmin)
