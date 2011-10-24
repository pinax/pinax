from pinax.apps.signup_codes.models import SignupCode


def stats():
    return {
        "signup_codes_total": SignupCode.objects.count(),
        "signup_codes_sent": SignupCode.objects.filter(sent__isnull=True).count(),
        "signup_codes_used": SignupCode.objects.filter(use_count__gt=0).count()
    }
