from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase

from django.contrib.auth.models import User


class ChangePasswordTest(TestCase):
    urls = "pinax.apps.account.tests.account_urls"
    
    def setUp(self):
        self.old_installed_apps = settings.INSTALLED_APPS
        # remove django-mailer to properly test for outbound email
        if "mailer" in settings.INSTALLED_APPS:
            settings.INSTALLED_APPS.remove("mailer")
        
        self.EMAIL_AUTHENTICATION = getattr(settings, "ACCOUNT_EMAIL_AUTHENTICATION", False)
        User.objects.create_user("bob", "bob@example.com", "abc123")
        
    
    def tearDown(self):
        settings.INSTALLED_APPS = self.old_installed_apps
    
    def test_password_change_view(self):
        """
        Test GET on /password_change/
        """
        response = self.client.get(reverse("acct_passwd"))
        self.assertEquals(response.status_code, 302)
        
    def test_authenticated_password_change_view(self):
        """
        Error if user can not login and get to the password change view
        """
        data = {
            "password": "abc123",
        }
        if self.EMAIL_AUTHENTICATION:
            data["email"] = "bob@example.com"
        else:
            data["username"] = "bob"
        
        response = self.client.post(reverse("acct_login"), data)
        self.assertEquals(response.status_code, 302)
        response = self.client.get(reverse("acct_passwd"))
        self.assertEquals(response.status_code, 200)
    
    def test_change_password(self):
        """
        Error if password can not be changed
        """
        bob = User.objects.get(email="bob@example.com")
        data = {
            "oldpassword": "abc123",
            "password1": "def456",
            "password2": "def456",
        }
        response = self.client.post(reverse("acct_passwd"), data)
        self.assertEquals(response.status_code, 302)
    
    def test_signal_password_change(self):
        """
        Two tests should pass here if the signal is fired.
        """
        from pinax.apps.account.signals import password_changed
        bob = User.objects.get(email="bob@example.com")

        def receiver(sender, user):
            self.assertEquals(user, bob)
            self.assert_(user.check_password("ghi789"))
        
        password_changed.connect(receiver)
        
        data = {
            "oldpassword": "def456",
            "password1": "ghi789",
            "password2": "ghi789",
        }
        response = self.client.post(reverse("acct_passwd"), data)
