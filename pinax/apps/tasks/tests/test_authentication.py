# coding: utf-8
from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase

from django.contrib.auth.models import User


class BaseTaskTest(TestCase):
    fixtures = ["test_tasks.json"]
    urls = "pinax.apps.tasks.tests.tasks_urls"
    
    def setUp(self):
        settings.MIDDLEWARE_CLASSES.append("pagination.middleware.PaginationMiddleware")
    
    def tearDown(self):
        settings.MIDDLEWARE_CLASSES.remove("pagination.middleware.PaginationMiddleware")


class AnonymousTaskTest(BaseTaskTest):
    def testAnonymousCannotEdit(self):
        """
        Anonymous users should not edit tasks
        """
        response = self.client.get(reverse("task_detail", args=[1]))
        self.failUnlessEqual(response.status_code, 200)
        self.failUnless(response.content.find("<h2>Edit</h2>") == -1,
            "Anonymous user is able to edit tasks.")


class AuthenticatedTaskTest(BaseTaskTest):
    def testMemberCanEdit(self):
        """
        Member users should be able to edit tasks
        """
        self.client.login(username="admin", password="test")
        response = self.client.get(reverse("task_detail", args=[1]))
        self.failUnlessEqual(response.status_code, 200)
        self.failUnless(response.content.find("<h2>Edit</h2>") != -1,
            "Authenticated users cannot edit tasks.")
        self.client.logout()
