import datetime
import os

from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.hashcompat import sha_constructor

import signup_codes

from signup_codes.models import SignupCode


class InviteUserTest(TestCase):
    
    urls = "signup_codes.tests.signup_codes_urls"
    
    def setUp(self):
        self.old_installed_apps = settings.INSTALLED_APPS
        # remove django-mailer to properly test for outbound email
        if "mailer" in settings.INSTALLED_APPS:
            settings.INSTALLED_APPS.remove("mailer")
        
        self.old_template_dirs = settings.TEMPLATE_DIRS
        
        settings.TEMPLATE_DIRS = [
            os.path.join(os.path.dirname(signup_codes.__file__), "tests", "templates"),
        ]
    
    def tearDown(self):
        settings.INSTALLED_APPS = self.old_installed_apps
        settings.TEMPLATE_DIRS = self.old_template_dirs
        
    def _create_user(self, username="tester", password="abc1234", email="test@example.com"):
        admin_user = User.objects.create_user(username, email, password)
        admin_user.save()
        
    def test_noauth_admin_invite_user(self):
        """
        Confirm that a user cannot submit an invitation without being
        authenticated as an admin user.
        """
        
        data = {"email":"bob@example.com"}
        
        # First they attempt without logging in
        response = self.client.post(reverse("admin_invite_user"), data)
        self.assertEqual(response.status_code, 302)
        
        # Then they attempt as a logged in user without admin rights.
        user = User.objects.create_user("joe_tester","joe@example.com", "tester")
        user.save()
        self.client.login(username="joe_tester", password="tester")
        response = self.client.post(reverse("admin_invite_user"), data)
        self.assertEqual(response.status_code, 302)
    
    def test_admin_invite_user(self):
        """
        Test on the admin invite user screen
        """
        
        # Create and authenticate a staff level user
        admin_user = User.objects.create_user("tester","bob@example.com", "tester")
        admin_user.save()
        admin_user.is_staff = True
        admin_user.save()
        
        self.client.login(username="tester", password="tester")
        
        # Now confirm that the invite is sent out by the staff level user
        data = {"email":"bob@example.com"}
        response = self.client.post(reverse("admin_invite_user"), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "An email has been sent to " + data["email"])
    
    def test_accept_invite(self):
        """
        test the user's ability to accept their token
        """
        
        #print help(self)
        # Create an invitation
        email = "joe@example.com"
        expiry = datetime.datetime.now() + datetime.timedelta(hours=1)
        code = sha_constructor("%s%s%s%s" % (
            settings.SECRET_KEY,
            email,
            str(expiry),
            settings.SECRET_KEY,
        )).hexdigest()
        signup_code = SignupCode(code=code, email=email, max_uses=1, expiry=expiry)
        signup_code.save()
        
        # First the invitee tries a bad signup_code
        data = { "code":"12345" }
        response = self.client.get(reverse("test_signup"), data)
        print response
        self.assertContains(response, "Incorrect Code")
        
        # Now they remember the code and try the right one
        data = { "code" : signup_code.code }
        response = self.client.get(reverse("test_signup"), data, follow=True)
        
        self.assertContains(response, "id_username")
        self.assertContains(response, "id_email")
        self.assertContains(response, "id_password")
        
        # User now creates their account
        data = { "username" : "joe",
                 "email": "joe@example.com",
                 "password1": "abc1234",
                 "password2": "abc1234",
                 "signup_code":signup_code.code,
                 "submit":"Sign Up &raquo;"
                }
        response = self.client.post(reverse("test_signup"), data, follow=True)
        print User.objects.all()
