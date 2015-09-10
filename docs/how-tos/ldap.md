# LDAP Integration

In your `requirements.txt`, add:

    django-auth-ldap==1.2.6

In your `settings.py`, add:

    AUTHENTICATION_BACKENDS = [
        "django_auth_ldap.backend.LDAPBackend",  # ldap will authenticate before your local database
        "account.auth_backends.UsernameAuthenticationBackend",
    ]

    import ldap
    from django_auth_ldap.config import LDAPSearch

    AUTH_LDAP_SERVER_URI = "ldap://127.0.0.1"
    AUTH_LDAP_USER_SEARCH = LDAPSearch(
        "ou=users,dc=example,dc=com",
        ldap.SCOPE_SUBTREE,
        "(uid=%(user)s)"
    )

The `AUTH_LDAP_*` settings will vary based on how LDAP is configured. For more
information, see the [django-auth-ldap documentation](https://pythonhosted.org/django-auth-ldap/).
