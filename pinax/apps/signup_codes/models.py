import datetime

from django.conf import settings
from django.core.mail import send_mail
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils.hashcompat import sha_constructor

from django.contrib.auth.models import User
from django.contrib.sites.models import Site

from pinax.apps.signup_codes.signals import signup_code_used


class SignupCode(models.Model):
    
    code = models.CharField(max_length=40)
    max_uses = models.PositiveIntegerField(default=0)
    expiry = models.DateTimeField(null=True, blank=True)
    inviter = models.ForeignKey(User, null=True, blank=True)
    email = models.EmailField(blank=True)
    notes = models.TextField(blank=True)
    sent = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(default=datetime.datetime.now, editable=False)
    
    # calculated
    use_count = models.PositiveIntegerField(editable=False, default=0)
    
    def __unicode__(self):
        return "%s [%s]" % (self.email, self.code)
    
    @classmethod
    def create(cls, email, expiry, group=None):
        expiry = datetime.datetime.now() + datetime.timedelta(hours=expiry)
        bits = [
            settings.SECRET_KEY,
            email,
            str(expiry),
        ]
        if group:
            bits.append("%s%s" % (group._meta, group.pk))
        code = sha_constructor("".join(bits)).hexdigest()
        return cls(code=code, email=email, max_uses=1, expiry=expiry)
    
    @classmethod
    def check(cls, code):
        if code:
            try:
                signup_code = cls._default_manager.get(code=code)
            except cls.DoesNotExist:
                return False
            else:
                # check max uses
                if signup_code.max_uses and signup_code.max_uses < signup_code.use_count + 1:
                    return False
                else:
                    if signup_code.expiry and datetime.datetime.now() > signup_code.expiry:
                        return False
                    else:
                        return signup_code
        else:
            return False
    
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
        signup_code_used.send(sender=result.__class__, signup_code_result=result)
    
    def send(self, group=None):
        current_site = Site.objects.get_current()
        domain = unicode(current_site.domain)
        ctx = {
            "group": group,
            "signup_code": self,
            "domain": domain,
        }
        subject = render_to_string("signup_codes/invite_user_subject.txt", ctx)
        message = render_to_string("signup_codes/invite_user.txt", ctx)
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [self.email])
        self.sent = datetime.datetime.now()
        self.save()


class SignupCodeResult(models.Model):
    
    signup_code = models.ForeignKey(SignupCode)
    user = models.ForeignKey(User)
    timestamp = models.DateTimeField(default=datetime.datetime.now)


@receiver(post_save, sender=SignupCodeResult)
def signup_code_result_save(sender, instance=None, created=False, **kwargs):
    if instance:
        signup_code = instance.signup_code
        signup_code.calculate_use_count()
