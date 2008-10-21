
import pytz

from django.conf import settings
from django import forms

from timezones.utils import adjust_datetime_to_timezone

TIMEZONE_CHOICES = tuple(zip(pytz.all_timezones, pytz.all_timezones))

class TimeZoneField(forms.ChoiceField):
    def __init__(self, choices=None,  max_length=None, min_length=None,
                 *args, **kwargs):
        self.max_length, self.min_length = max_length, min_length
        if choices is not None:
            kwargs["choices"] = choices
        else:
            kwargs["choices"] = TIMEZONE_CHOICES
        super(TimeZoneField, self).__init__(*args, **kwargs)

    def clean(self, value):
        value = super(TimeZoneField, self).clean(value)
        return pytz.timezone(value)

class LocalizedDateTimeField(forms.DateTimeField):
    """
    Converts the datetime from the user timezone to settings.TIME_ZONE.
    """
    def __init__(self, timezone=None, *args, **kwargs):
        super(LocalizedDateTimeField, self).__init__(*args, **kwargs)
        self.timezone = timezone or settings.TIME_ZONE
        
    def clean(self, value):
        value = super(LocalizedDateTimeField, self).clean(value)
        return adjust_datetime_to_timezone(value, from_tz=self.timezone)
