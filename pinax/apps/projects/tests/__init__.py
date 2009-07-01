from django.test import TestCase

from projects.models import Project

class ProjectsTest(TestCase):
    fixtures = ["projects_auth.json"]
    
    def test_unauth_create_get(self):
        """can an unauth'd user get to page?"""
        
        response = self.client.get("/projects/create/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["location"], "http://testserver/account/login?next=/projects/create/")
    
    def test_auth_create_get(self):
        """can an auth'd user get to page?"""
        
        logged_in = self.client.login(username="tester", password="tester")
        self.assertTrue(logged_in)
        response = self.client.get("/projects/create/")
        self.assertEqual(response.status_code, 200)
    
    def test_unauth_create_post(self):
        """can an unauth'd user post to create a new project?"""
        
        response = self.client.post("/projects/create/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["location"], "http://testserver/account/login?next=/projects/create/")
    
    def test_auth_create_post(self):
        """can an auth'd user post to create a new project?"""
        
        logged_in = self.client.login(username="tester", password="tester")
        self.assertTrue(logged_in)
        response = self.client.post("/projects/create/", {
            "slug": "test",
            "name": "Test Project",
            "description": "A test project.",
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["location"], "http://testserver/projects/project/test/")
        self.assertEqual(Project.objects.get(slug="test").creator.username, "tester")
    
    def test_auth_creator_membership(self):
        """is membership for creator correct?"""
        
        logged_in = self.client.login(username="tester", password="tester")
        self.assertTrue(logged_in)
        response = self.client.post("/projects/create/", {
            "slug": "test",
            "name": "Test Project",
            "description": "A test project.",
        })
        response = self.client.get("/projects/project/test/")
        self.assertEqual(Project.objects.get(slug="test").creator.username, "tester")
        self.assertEqual(len(Project.objects.get(slug="test").members.all()), 1)
        self.assertEqual(Project.objects.get(slug="test").members.all()[0].user.username, "tester")
        self.assertEqual(response.context[0]["is_member"], True)
