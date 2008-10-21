
from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

try:
    from notification import models as notification
except ImportError:
    notification = None

from announcements.models import Announcement

class AnnouncementAdminForm(forms.ModelForm):
    """
    A custom form for the admin of the Announcment model. Has an extra field
    called send_now that when checked will send out the announcment allowing
    the user to decide when that happens.
    """
    send_now = forms.BooleanField(required=False,
        help_text=_("Send out this announcement now."))
    
    class Meta:
        model = Announcement
    
    def save(self, commit=True):
        """
        Checks the send_now field in the form and when True sends out the
        announcement through notification if present.
        """
        announcement = super(AnnouncementAdminForm, self).save(commit)
        if self.cleaned_data["send_now"]:
            if notification:
                users = User.objects.all()
                notification.send(users, "announcement", {
                    "announcement": announcement,
                }, on_site=False, queue=True)
        return announcement
