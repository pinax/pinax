import re

from django.conf import settings
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase

from django.contrib.auth.models import User

from emailconfirmation.models import EmailAddress


test_urls = getattr(settings, "ROOT_URLCONF")
if not test_urls:
    test_urls = "pinax.apps.account.tests.account_urls"


class PasswordResetTest(TestCase):
    # tests based on django.contrib.auth tests
    
    urls = test_urls
    
    def setUp(self):
        self.old_installed_apps = settings.INSTALLED_APPS
        # remove django-mailer to properly test for outbound email
        if "mailer" in settings.INSTALLED_APPS:
            settings.INSTALLED_APPS.remove("mailer")
    
    def tearDown(self):
        settings.INSTALLED_APPS = self.old_installed_apps
    
    def context_lookup(self, response, key):
        # used for debugging
        for subcontext in response.context:
            if key in subcontext:
                return subcontext[key]
        raise KeyError
    
    def test_password_reset_view(self):
        """
        Test GET on /password_reset/
        """
        response = self.client.get(reverse("acct_passwd_reset"))
        self.assertEquals(response.status_code, 200)
    
    def test_email_not_found(self):
        """
        Error is raised if the provided email address isn't verified to an
        existing user account
        """
        data = {
            "email": "nothing@example.com",
        }
        response = self.client.post(reverse("acct_passwd_reset"), data)
        self.assertEquals(response.status_code, 200)
        # @@@ instead of hard-coding this error message rely on a error key
        # defined in the form where the site developer would override this
        # error message.
        self.assertContains(response, "Email address not verified for any user account")
        self.assertEquals(len(mail.outbox), 0)
    
    def test_email_not_verified(self):
        """
        Error is raised if the provided email address isn't verified to an
        existing user account
        """
        bob = User.objects.create_user("bob", "bob@example.com", "abc123")
        EmailAddress.objects.create(
            user = bob,
            email = "bob@example.com",
            verified = False,
            primary = True,
        )
        data = {
            "email": "bob@example.com",
        }
        response = self.client.post(reverse("acct_passwd_reset"), data)
        self.assertEquals(response.status_code, 200)
        # @@@ instead of hard-coding this error message rely on a error key
        # defined in the form where the site developer would override this
        # error message.
        self.assertContains(response, "Email address not verified for any user account")
        self.assertEquals(len(mail.outbox), 0)
    
    def test_email_found(self):
        """
        Email is sent if a valid email address is provided for password reset
        """
        bob = User.objects.create_user("bob", "bob@example.com", "abc123")
        EmailAddress.objects.create(
            user = bob,
            email = "bob@example.com",
            verified = True,
            primary = True,
        )
        
        data = {
            "email": "bob@example.com",
        }
        response = self.client.post(reverse("acct_passwd_reset"), data)
        self.assertEquals(response.status_code, 302)
        self.assertEquals(len(mail.outbox), 1)
    
    def _read_reset_email(self,  email):
        match = re.search(r"https?://[^/]*(/.*reset_key/\S*)", email.body)
        self.assert_(match is not None, "No URL found in sent email")
        return match.group(), match.groups()[0]
    
    def _test_confirm_start(self):
        bob = User.objects.create_user("bob", "bob@example.com", "abc123")
        EmailAddress.objects.create(
            user = bob,
            email = "bob@example.com",
            verified = True,
            primary = True,
        )
        
        data = {
            "email": "bob@example.com",
        }
        response = self.client.post(reverse("acct_passwd_reset"), data)
        self.assertEquals(response.status_code, 302)
        self.assertEquals(len(mail.outbox), 1)
        return self._read_reset_email(mail.outbox[0])
    
    def test_confirm_invalid(self):
        url, path = self._test_confirm_start()
        
        # munge the token in the path, but keep the same length, in case the
        # URLconf will reject a different length.
        path = path[:-5] + ("0"*4) + path[-1]
        
        response = self.client.get(path)
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "The password reset link was invalid")
    
    def test_confirm_valid(self):
        url, path = self._test_confirm_start()
        response = self.client.get(path)
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "New Password (again)")
    
    def test_confirm_invalid_post(self):
        url, path = self._test_confirm_start()
        
        # munge the token in the path, but keep the same length, in case the
        # URLconf will reject a different length.
        path = path[:-5] + ("0"*4) + path[-1]
        
        data = {
            "password1": "newpassword",
            "password2": "newpassword",
        }
        response = self.client.post(path, data)
        user = User.objects.get(email="bob@example.com")
        self.assert_(not user.check_password("newpassword"))
    
    def test_confirm_complete(self):
        url, path = self._test_confirm_start()
        
        data = {
            "password1": "newpassword",
            "password2": "newpassword",
        }
        response = self.client.post(path, data)
        self.assertEquals(response.status_code, 200)
        # check the password has been changed
        user = User.objects.get(email="bob@example.com")
        self.assert_(user.check_password("newpassword"))
        
        # check we can't GET with same path
        response = self.client.get(path)
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "The password reset link was invalid")
        
        # check we can't POST with same path
        data = {
            "password1": "anothernewpassword",
            "password2": "anothernewpassword",
        }
        response = self.client.post(path)
        self.assertEquals(response.status_code, 200)
        user = User.objects.get(email="bob@example.com")
        self.assert_(not user.check_password("anothernewpassword"))
    
    def test_confirm_different_passwords(self):
        url, path = self._test_confirm_start()
        
        data = {
            "password1": "newpassword",
            "password2": "anothernewpassword",
        }
        response = self.client.post(path, data)
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "You must type the same password each time.")

