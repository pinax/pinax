from django.core.management.base import NoArgsCommand
from profiles.models import Profile
from account.models import Account, OtherServiceInfo
from django.contrib.auth.models import User
from django.conf import settings

class Command(NoArgsCommand):
    help = 'Create an account object for users which do not have one and copy over info from profile.'
    
    def handle_noargs(self, **options):
        
        for user in User.objects.all():
            profile = Profile.objects.get(user=user)
            account, created = Account.objects.get_or_create(user=user)
            
            if created:
                account.timezone = profile.timezone
                account.language = account.language
                account.save()
                print "created account for %s" % user
                
                if profile.blogrss:
                    OtherServiceInfo(user=user, key="blogrss", value=profile.blogrss).save()
                if profile.twitter_user:
                    OtherServiceInfo(user=user, key="twitter_user", value=profile.twitter_user).save()
                if profile.twitter_password:
                    OtherServiceInfo(user=user, key="twitter_password", value=profile.twitter_password).save()
                if profile.pownce_user:
                    OtherServiceInfo(user=user, key="pownce_user", value=profile.pownce_user).save()
                if profile.pownce_password:
                    OtherServiceInfo(user=user, key="pownce_password", value=profile.pownce_password).save()
