
from datetime import datetime

from django.db import models
from django.db.models.signals import post_save

from django.contrib.auth.models import User

class SignupCode(models.Model):
    """
    """
    code = models.CharField(max_length=40)
    max_uses = models.PositiveIntegerField(default=0)
    expiry = models.DateTimeField(null=True, blank=True)
    inviter = models.ForeignKey(User, null=True, blank=True)
    email = models.EmailField(blank=True)
    notes = models.TextField(blank=True)
    created = models.DateTimeField(default=datetime.now, editable=False)
    
    # calculated
    use_count = models.PositiveIntegerField(editable=False, default=0)
    
    def __unicode__(self):
        return self.code
    
    def calculate_use_count(self):
        self.use_count = self.signupcoderesult_set.count()
        self.save()
    
    def use(self, user):
        """
        Add a SignupCode result attached to the given user.
        """
        result = SignupCodeResult()
        result.signup_code = self
        result.user = user
        result.save()
    

class SignupCodeResult(models.Model):
    """
    """
    signup_code = models.ForeignKey(SignupCode)
    user = models.ForeignKey(User)
    timestamp = models.DateTimeField(default=datetime.now)


def signup_code_result_save(sender, instance=None, created=False, **kwargs):
    if instance:
        signup_code = instance.signup_code
        signup_code.calculate_use_count()

post_save.connect(signup_code_result_save, sender=SignupCodeResult)


def check_signup_code(code):
    if code:
        try:
            signup_code = SignupCode.objects.get(code=code)
        except SignupCode.DoesNotExist:
            return False
        else:
            # check max uses
            if signup_code.max_uses and signup_code.max_uses < signup_code.use_count + 1:
                return False
            else:
                if signup_code.expiry and datetime.now() > signup_code.expiry:
                    return False
                else:
                    return signup_code
    else:
        return False
