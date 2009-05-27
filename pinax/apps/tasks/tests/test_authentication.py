# coding: utf-8

from django.test import TestCase
from django.contrib.auth.models import User

class AnonymousTaskTest(TestCase):
    fixtures = ['test_tasks.json']

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testAnonymousCannotEdit(self):
        """Anonymous users should not edit tasks"""
        response = self.client.get('/tasks/task/1/')
        self.failUnlessEqual(response.status_code, 200)
        self.failUnless(response.content.find('<h2>Edit</h2>') == -1,
            'Anonymous user is able to edit tasks.')


class AuthenticatedTaskTest(TestCase):
    fixtures = ['test_tasks.json']

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testMemberCanEdit(self):
        """Member users should be able to edit tasks"""
        self.client.login(username='admin', password='test')
        response = self.client.get('/tasks/task/1/')
        self.failUnlessEqual(response.status_code, 200)
        self.failUnless(response.content.find('<h2>Edit</h2>') != -1,
            'Authenticated users cannot edit tasks.')
        self.client.logout()
