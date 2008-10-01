from django.core.management.base import NoArgsCommand, CommandError
from django.contrib.auth.models import User
from django.conf import settings
from account.models import Account, OtherServiceInfo

class Command(NoArgsCommand):
    help = 'Create an account object for users which do not have one and copy over info from profile.'
    
    def handle_noargs(self, **options):
        try:
            from profiles.models import Profile
        except ImportError:
            raise CommandError("The profile app could not be imported.")
        
        for user in User.objects.all():
            profile = Profile.objects.get(user=user)
            account, created = Account.objects.get_or_create(user=user)
            
            if created:
                account.timezone = profile.timezone
                account.language = account.language
                account.save()
                print "created account for %s" % user
            
            if profile.blogrss:
                info, created = OtherServiceInfo.objects.get_or_create(user=user, key="blogrss")
                info.value = profile.blogrss
                info.save()
                print "copied over blogrss for %s" % user
            if profile.twitter_user:
                info, created = OtherServiceInfo.objects.get_or_create(user=user, key="twitter_user")
                info.value = profile.twitter_user
                info.save()
                print "copied over twitter_user for %s" % user
            if profile.twitter_password:
                info, created = OtherServiceInfo.objects.get_or_create(user=user, key="twitter_password")
                info.value = profile.twitter_password
                info.save()
                print "copied over twitter_password for %s" % user
            if profile.pownce_user:
                info, created = OtherServiceInfo.objects.get_or_create(user=user, key="pownce_user")
                info.value = profile.pownce_user
                info.save()
                print "copied over pownce_user for %s" % user
            if profile.pownce_password:
                info, created = OtherServiceInfo.objects.get_or_create(user=user, key="pownce_password")
                info.value = profile.pownce_password
                info.save()
                print "copied over pownce_password for %s" % user
