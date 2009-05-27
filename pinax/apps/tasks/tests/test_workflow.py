# coding: utf-8

from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.test import TestCase

from tasks.models import Task
from tasks.workflow import always, is_assignee, is_assignee_or_none
from tasks.workflow import is_creator, no_assignee, is_task_manager
from tasks.workflow import OR
from tasks.workflow import TASK_MANAGER

class TestWorkflowFunctions(TestCase):
    fixtures = ['test_tasks.json']
    
    def setUp(self):
        self.user_admin = User.objects.get(username__exact='admin')
        self.user_joe = User.objects.get(username__exact='joe')
        self.user_sam = User.objects.get(username__exact='sam')
        
        # The task is assigned to user joe by user admin
        self.task = Task.objects.get(pk__exact=1)
        self.task.assignee = self.user_joe
        self.task.save()
        
        # lets set up a sample group
        self.group = Group(name=TASK_MANAGER)
        self.group.save()
        self.group.user_set.add(self.user_admin)
    
    
    def tearDown(self):
        pass
    
    def test_always(self):
        self.assertEquals(True, always(self.task, self.user_admin))
        self.assertEquals(True, always(self.task, self.user_joe))
        self.assertEquals(True, always(self.task, None))
    
    def test_is_assignee(self):
        self.assertEquals(False, is_assignee(self.task, self.user_admin))
        self.assertEquals(True, is_assignee(self.task, self.user_joe))
        self.assertEquals(False, is_assignee(self.task, None))
    
    def test_is_assignee_or_none(self):
        # normal test
        self.assertEquals(False, is_assignee_or_none(self.task, self.user_admin))
        self.assertEquals(True, is_assignee_or_none(self.task, self.user_joe))
        self.assertEquals(False, is_assignee_or_none(self.task, None))
        
        # now lets remove the assignee and see what happens
        self.task.assignee = None
        self.task.save()
        self.assertEquals(True, is_assignee_or_none(self.task, self.user_admin))
        self.assertEquals(True, is_assignee_or_none(self.task, self.user_joe))
        self.assertEquals(True, is_assignee_or_none(self.task, None))
    
    def test_is_creator(self):
        self.assertEquals(True, is_creator(self.task, self.user_admin))
        self.assertEquals(False, is_creator(self.task, self.user_joe))
        self.assertEquals(False, is_creator(self.task, None))
    
    def test_is_no_assignee(self):
        # test first with assignee
        self.assertEquals(False, no_assignee(self.task, self.user_admin))
        self.assertEquals(False, no_assignee(self.task, self.user_joe))
        self.assertEquals(False, no_assignee(self.task, None))
        
        # test again without assignee
        self.task.assignee = None
        self.task.save()
        self.assertEquals(True, no_assignee(self.task, self.user_admin))
        self.assertEquals(True, no_assignee(self.task, self.user_joe))
        self.assertEquals(True, no_assignee(self.task, None))
    
    def test_is_task_manager(self):
        self.assertEquals(True, is_task_manager(self.task, self.user_admin))
        self.assertEquals(False, is_task_manager(self.task, self.user_joe))
        self.assertEquals(False, is_task_manager(self.task, None))
    
    def test_OR(self):
        self.assertEquals(True, OR(is_creator, is_assignee)(self.task, self.user_admin))
        self.assertEquals(True, OR(is_creator, is_assignee)(self.task, self.user_joe))
        self.assertEquals(False, OR(is_creator, is_assignee)(self.task, None))
        self.assertEquals(False, OR(is_creator, is_assignee)(self.task, self.user_sam))
        