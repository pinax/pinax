from django.contrib import admin
from emailconfirmation.models import EmailAddress, EmailConfirmation

admin.site.register(EmailAddress)
admin.site.register(EmailConfirmation)
