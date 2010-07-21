from django.conf import settings

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User


class AuthenticationBackend(ModelBackend):
    
    def authenticate(self, **credentials):
        lookup_params = {}
        if settings.ACCOUNT_EMAIL_AUTHENTICATION:
            lookup_params["email"] = credentials["email"]
        else:
            lookup_params["username"] = credentials["username"]
        try:
            user = User.objects.get(**lookup_params)
        except User.DoesNotExist:
            return None
        else:
            if user.check_password(credentials["password"]):
                return user


EmailModelBackend = AuthenticationBackend