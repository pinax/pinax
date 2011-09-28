from django import forms

from pinax.apps.waitinglist.models import WaitingListEntry


class WaitingListEntryForm(forms.ModelForm):
    
    class Meta:
        model = WaitingListEntry
    
    def clean_email(self):
        value = self.cleaned_data["email"]
        try:
            entry = WaitingListEntry.objects.get(email=value)
        except WaitingListEntry.DoesNotExist:
            return value
        else:
            raise forms.ValidationError("The email address %(email)s already "
                "registered on %(date)s." % {
                    "email": value,
                    "date": entry.created.strftime("%m/%d/%y"),
                }
            )
