import datetime
from django.test import TestCase
from django.contrib.auth.models import User
from messages.models import Message

class SendTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user('user1', 'user1@example.com', '123456')
        self.user2 = User.objects.create_user('user2', 'user2@example.com', '123456')
        self.msg1 = Message(sender=self.user1, recipient=self.user2, subject='Subject Text', body='Body Text')
        self.msg1.save()
        
    def testBasic(self):
        self.assertEquals(self.msg1.sender, self.user1)
        self.assertEquals(self.msg1.recipient, self.user2)
        self.assertEquals(self.msg1.subject, 'Subject Text')
        self.assertEquals(self.msg1.body, 'Body Text')
        self.assertEquals(self.user1.sent_messages.count(), 1)
        self.assertEquals(self.user1.received_messages.count(), 0)
        self.assertEquals(self.user2.received_messages.count(), 1)
        self.assertEquals(self.user2.sent_messages.count(), 0)
        
class DeleteTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user('user3', 'user3@example.com', '123456')
        self.user2 = User.objects.create_user('user4', 'user4@example.com', '123456')
        self.msg1 = Message(sender=self.user1, recipient=self.user2, subject='Subject Text 1', body='Body Text 1')
        self.msg2 = Message(sender=self.user1, recipient=self.user2, subject='Subject Text 2', body='Body Text 2')
        self.msg1.sender_deleted_at = datetime.datetime.now()
        self.msg2.recipient_deleted_at = datetime.datetime.now()
        self.msg1.save()
        self.msg2.save()
                
    def testBasic(self):
        self.assertEquals(self.user1.sent_messages.count(), 1)
        self.assertEquals(self.user1.sent_messages.all()[0].subject, 'Subject Text 2')
        self.assertEquals(self.user2.received_messages.count(),1)
        self.assertEquals(self.user2.received_messages.all()[0].subject, 'Subject Text 1')
        #undelete
        self.msg1.sender_deleted_at = None
        self.msg2.recipient_deleted_at = None
        self.msg1.save()
        self.msg2.save()
        self.assertEquals(self.user1.sent_messages.count(), 2)
        self.assertEquals(self.user2.received_messages.count(),2)
        