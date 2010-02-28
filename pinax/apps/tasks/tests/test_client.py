# coding: utf-8
from django.core.urlresolvers import reverse
from django.test import TestCase


# @@ docutils 0.6 omits the first header
rst_markup = """
Sample Header
===============

Blah blah blah

Lower Header
-------------

Blah blah blah
"""


class TestAddForm(TestCase):
    fixtures = ["test_tasks.json"]
    urls = "pinax.apps.tasks.tests.tasks_urls"
    
    def setUp(self):
        self.client.login(username="admin", password="test")
    
    def tearDown(self):
        pass
    
    def test_add_buttons(self):
        response = self.client.get(reverse("task_add"))
        
        # Check that the response is 200 OK.
        self.failUnlessEqual(response.status_code, 200)
        
        # check that there is an add button
        self.assertContains(response, '<input type="submit" value="Add task"/>')
        
        # check that there is an add another task button
        self.assertContains(response, "add-another-task")
    
    def test_markup(self):
        
        # create some sample form data
        form_data = {
            "summary": "my simple test",
            "detail": rst_markup,
            "markup": "restructuredtext",
            "assignee": "",
            "tags": ""
        }
        
        # post the form
        response = self.client.post(reverse("task_add"), form_data)
        
        # display the resultant task
        response = self.client.get(reverse("task_detail", args=[3]))
        
        # test the markup
        self.assertContains(response, '<p>Blah blah blah</p>')
    
    def test_tag_for_rel(self):
        #  checking for tag
        response = self.client.get(reverse("task_list"))
        self.assertContains(response, '<a rel="tag" href="/tasks/tag/test/">test</a>')
        
