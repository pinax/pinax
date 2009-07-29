from django.test import TestCase

from basic_groups.models import BasicGroup

class BasicGroupsTest(TestCase):
    fixtures = ["basic_groups_auth.json"]
    
    def test_unauth_create_get(self):
        """can an unauth'd user get to page?"""
        
        response = self.client.get("/groups/create/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["location"], "http://testserver/account/login?next=/groups/create/")
    
    def test_auth_create_get(self):
        """can an auth'd user get to page?"""
        
        logged_in = self.client.login(username="tester", password="tester")
        self.assertTrue(logged_in)
        response = self.client.get("/groups/create/")
        self.assertEqual(response.status_code, 200)
    
    def test_unauth_create_post(self):
        """can an unauth'd user post to create a new group?"""
        
        response = self.client.post("/groups/create/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["location"], "http://testserver/account/login?next=/groups/create/")
    
    def test_auth_create_post(self):
        """can an auth'd user post to create a new group?"""
        
        logged_in = self.client.login(username="tester", password="tester")
        self.assertTrue(logged_in)
        response = self.client.post("/groups/create/", {
            "slug": "test",
            "name": "Test Group",
            "description": "A test group.",
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["location"], "http://testserver/groups/group/test/")
        self.assertEqual(BasicGroup.objects.get(slug="test").creator.username, "tester")
        self.assertEqual(BasicGroup.objects.get(slug="test").members.all()[0].username, "tester")
    
    def test_auth_creator_membership(self):
        """is membership for creator correct?"""
        
        logged_in = self.client.login(username="tester", password="tester")
        self.assertTrue(logged_in)
        response = self.client.post("/groups/create/", {
            "slug": "test",
            "name": "Test Group",
            "description": "A test group.",
        })
        response = self.client.get("/groups/group/test/")
        self.assertEqual(BasicGroup.objects.get(slug="test").creator.username, "tester")
        self.assertEqual(BasicGroup.objects.get(slug="test").members.all()[0].username, "tester")
        self.assertEqual(response.context[0]["is_member"], True)
