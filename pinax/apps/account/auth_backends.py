from django.conf import settings

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User


class AuthenticationBackend(ModelBackend):
    
    def authenticate(self, **credentials):
        lookup_params = {}
        if settings.ACCOUNT_EMAIL_AUTHENTICATION:
            name, identity = "email", credentials.get("email")
        else:
            name, identity = "username", credentials.get("username")
        if identity is None:
            return None
        lookup_params[name] = identity
        try:
            user = User.objects.get(**lookup_params)
        except User.DoesNotExist:
            return None
        else:
            if user.check_password(credentials["password"]):
                return user
    
    def has_perm(self, user, perm):
        # @@@ allow all users to add wiki pages
        wakawaka_perms = [
            "wakawaka.add_wikipage",
            "wakawaka.add_revision",
            "wakawaka.change_wikipage",
            "wakawaka.change_revision"
        ]
        if perm in wakawaka_perms:
            return True
        return super(AuthenticationBackend, self).has_perm(user, perm)


EmailModelBackend = AuthenticationBackend