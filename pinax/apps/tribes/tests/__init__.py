from django.core.urlresolvers import reverse
from django.test import TestCase

from pinax.apps.tribes.models import Tribe

class TribesTest(TestCase):
    fixtures = ["tribes_auth.json"]
    urls = "pinax.apps.tribes.tests.tribes_urls"
    
    def test_unauth_create_get(self):
        """
        can an unauth'd user get to page?
        """
        
        response = self.client.get(reverse("tribe_create"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["location"], "http://testserver/account/login/?next=%s" % reverse("tribe_create"))
    
    def test_auth_create_get(self):
        """
        can an auth'd user get to page?
        """
        
        logged_in = self.client.login(username="tester", password="tester")
        self.assertTrue(logged_in)
        response = self.client.get(reverse("tribe_create"))
        self.assertEqual(response.status_code, 200)
    
    def test_unauth_create_post(self):
        """
        can an unauth'd user post to create a new tribe?
        """
        
        response = self.client.post(reverse("tribe_create"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["location"], "http://testserver/account/login/?next=%s" % reverse("tribe_create"))
    
    def test_auth_create_post(self):
        """
        can an auth'd user post to create a new tribe?
        """
        
        logged_in = self.client.login(username="tester", password="tester")
        self.assertTrue(logged_in)
        response = self.client.post(reverse("tribe_create"), {
            "slug": "test",
            "name": "Test Tribe",
            "description": "A test tribe.",
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["location"], "http://testserver/tribes/tribe/test/")
        self.assertEqual(Tribe.objects.get(slug="test").creator.username, "tester")
        self.assertEqual(Tribe.objects.get(slug="test").members.all()[0].username, "tester")
    
    def test_auth_creator_membership(self):
        """
        is membership for creator correct?
        """
        
        logged_in = self.client.login(username="tester", password="tester")
        self.assertTrue(logged_in)
        response = self.client.post(reverse("tribe_create"), {
            "slug": "test",
            "name": "Test Tribe",
            "description": "A test tribe.",
        })
        response = self.client.get(reverse("tribe_detail", args=["test"]))
        self.assertEqual(Tribe.objects.get(slug="test").creator.username, "tester")
        self.assertEqual(Tribe.objects.get(slug="test").members.all()[0].username, "tester")
        self.assertEqual(response.context[0]["is_member"], True)
