import django.dispatch



account_user_signed_up = django.dispatch.Signal(providing_args=["user"])