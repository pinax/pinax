from datetime import datetime

from django.db import models


PRIORITIES = (
    ('1', 'high'),
    ('2', 'medium'),
    ('3', 'low'),
    ('4', 'deferred'),
)



class MessageManager(models.Manager):
    
    def high_priority(self):
        """
        the high priority messages in the queue
        """
        
        return self.filter(priority='1')
    
    def medium_priority(self):
        """
        the medium priority messages in the queue
        """
        
        return self.filter(priority='2')
    
    def low_priority(self):
        """
        the low priority messages in the queue
        """
        
        return self.filter(priority='3')
    
    def non_deferred(self):
        """
        the messages in the queue not deferred
        """
        
        return self.filter(priority__lt='4')
    
    def deferred(self):
        """
        the deferred messages in the queue
        """
    
        return self.filter(priority='4')
    
    def retry_deferred(self, new_priority=2):
        count = 0
        for message in self.deferred():
            if message.retry(new_priority):
                count += 1
        return count


class Message(models.Model):
    
    objects = MessageManager()
    
    to_address = models.CharField(max_length=50)
    from_address = models.CharField(max_length=50)
    subject = models.CharField(max_length=100)
    message_body = models.TextField()
    when_added = models.DateTimeField(default=datetime.now)
    priority = models.CharField(max_length=1, choices=PRIORITIES, default='2')
    # @@@ campaign?
    # @@@ content_type?
    
    def defer(self):
        self.priority = '4'
        self.save()
    
    def retry(self, new_priority=2):
        if self.priority == '4':
            self.priority = new_priority
            self.save()
            return True
        else:
            return False
    

class DontSendEntryManager(models.Manager):
    
    def has_address(self, address):
        """
        is the given address on the don't send list?
        """
        
        if self.filter(to_address=address).count() > 0: # @@@ is there a better way?
            return True
        else:
            return False


class DontSendEntry(models.Model):
    
    objects = DontSendEntryManager()
    
    to_address = models.CharField(max_length=50)
    when_added = models.DateTimeField()
    # @@@ who added?
    # @@@ comment field?
    
    class Meta:
        verbose_name = 'don\'t send entry'
        verbose_name_plural = 'don\'t send entries'
    

RESULT_CODES = (
    ('1', 'success'),
    ('2', 'don\'t send'),
    ('3', 'failure'),
    # @@@ other types of failure?
)



class MessageLogManager(models.Manager):
    
    def log(self, message, result_code, log_message = ''):
        """
        create a log entry for an attempt to send the given message and
        record the given result and (optionally) a log message
        """
        
        message_log = self.create(
            to_address = message.to_address,
            from_address = message.from_address,
            subject = message.subject,
            message_body = message.message_body,
            when_added = message.when_added,
            priority = message.priority,
            # @@@ other fields from Message
            result = result_code,
            log_message = log_message,
        )
        message_log.save()


class MessageLog(models.Model):
    
    objects = MessageLogManager()
    
    # fields from Message
    to_address = models.CharField(max_length=50)
    from_address = models.CharField(max_length=50)
    subject = models.CharField(max_length=100)
    message_body = models.TextField()
    when_added = models.DateTimeField()
    priority = models.CharField(max_length=1, choices=PRIORITIES)
    # @@@ campaign?
    
    # additional logging fields
    when_attempted = models.DateTimeField(default=datetime.now)
    result = models.CharField(max_length=1, choices=RESULT_CODES)
    log_message = models.TextField()
    
