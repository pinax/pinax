import django.dispatch

# @@@ this is the exact same as in django.contrib.auth not sure why it's duped here
user_logged_in = django.dispatch.Signal(providing_args=["request", "user"])

password_changed = django.dispatch.Signal(providing_args=["user",])
user_login_attempt = django.dispatch.Signal(providing_args=["username", "result"])
user_sign_up_attempt = django.dispatch.Signal(providing_args=["username",  "email", "result"])
user_signed_up = django.dispatch.Signal(providing_args=["user"])

timezone_changed = django.dispatch.Signal(providing_args=["request", "from_timezone", "to_timezone"])
