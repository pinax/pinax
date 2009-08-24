# coding: utf-8

from django.contrib.auth.models import User
from django.test import TestCase

from tasks.models import Task, TaskHistory, Nudge

class TestTask(TestCase):
    fixtures = ['test_tasks.json']
    
    def setUp(self):
        self.task = Task.objects.get(pk__exact=1)
        self.other_task = Task.objects.get(pk__exact=2)
        self.user_admin = User.objects.get(username__exact='admin')
        self.user_joe = User.objects.get(username__exact='joe')
        
        self.task_nudge_count = 2
        self.other_task_nudge_count = 1
    
    def tearDown(self):
        pass
    
    def test_allowable_states(self):
        """Doing some simple assertions based off states"""
        
        # TODO: Add more state checks
        
        # Task is just created
        states = self.task.allowable_states(self.user_admin)
        self.assertEquals(states,
            [('1', 'leave open')])
        
        # Now we assign it. This is what the assignee sees
        self.task.assignee = self.user_joe
        self.task.save()
        states = self.task.allowable_states(self.user_joe)
        self.assertEquals(states, [('1', 'leave open')])
        
        # this is what the creator sees
        states = self.task.allowable_states(self.user_admin)
        self.assertEquals(states, [('1', 'leave open')])
        
        # Task is now moved to in-progress. this is what the assignee can see.
        self.task.state = "4"
        self.task.save()
        states = self.task.allowable_states(self.user_joe)
        self.assertEquals(states,
            [('4', 'still in progress'), ('5', 'discussion needed'),
            ('8', 'fix needs review')] )
            
    def test_denudge(self):
        """ We check that:
            1. We have nudges across multiple tasks.
            2. After denudging the task, the task has no more nudges
            3. After denudging the task, the other task still has nudges
        """
        
        # we have nudges across multiple tasks including our sample task
        self.assertEquals(len(self.task.task_nudge.all()), self.task_nudge_count)
        self.assertEquals(len(self.other_task.task_nudge.all()), self.other_task_nudge_count)
        
        # now we denudge our task
        self.task.denudge()
        
        # Our task should have no nudges
        self.assertEquals(len(self.task.task_nudge.all()), 0)
        
        # The other task should have its original number of nudges
        self.assertEquals(len(self.other_task.task_nudge.all()), self.other_task_nudge_count)


class TestTaskHistory(TestCase):
    fixtures = ['test_tasks.json']
    
    def setUp(self):
        self.task = Task.objects.get(pk__exact=1)
        self.user_admin = User.objects.get(username__exact='admin')
        self.user_joe = User.objects.get(username__exact='joe')
    
    def tearDown(self):
        pass
    
    def test_history(self):
        """ lets see if history tracks user changes if done against the task"""
        
        # we have admin assign joe to the task.
        self.task.assignee = self.user_joe
        self.task.save()
        self.task.save_history(change_owner=self.user_admin)
        
        # fetch the history
        history = self.task.history_task.all()[0]
        
        # The task assignee should be joe
        self.assertEquals(history.assignee, self.user_joe)
        
        # the person who made the change was admin
        self.assertEquals(history.owner, self.user_admin)
        
    def test_change_history_by_non_creator(self):
        """ In CPC task 173 non-comment changes by users besides the task
        creator don't save the current user. This checks to see that the history
        is changed accurately.
        """
        
        # we have joe assign himself to a task that admin created
        self.task.assignee = self.user_joe
        self.task.save()
        self.task.save_history(change_owner=self.user_joe)
        
        # fetch the history
        history = self.task.history_task.all()[0]

        # the person who made the change was joe
        self.assertEquals(history.owner, self.user_joe)
