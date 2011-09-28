import django.dispatch


signup_code_used = django.dispatch.Signal(providing_args=["signup_code_result"])
