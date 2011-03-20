import django.dispatch


user_logged_in = django.dispatch.Signal(providing_args=["request", "user"])
password_changed = django.dispatch.Signal(providing_args=["user",])