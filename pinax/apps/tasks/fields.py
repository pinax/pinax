from django.conf import settings
from django.db import models



MARKUP_DEFAULT_FILTER = getattr(settings, "MARKUP_DEFAULT_FILTER", None)
MARKUP_CHOICES = getattr(settings, "MARKUP_CHOICES", [])



# @@@ the behavior here should be available in django-markup
class MarkupField(models.CharField):
    
    def __init__(self, *args, **kwargs):
        kwargs["max_length"] = kwargs.get("max_length", 20)
        self.markup_default_filter = kwargs.get("default") or MARKUP_DEFAULT_FILTER
        if self.markup_default_filter:
            kwargs["default"] = self.markup_default_filter
        else:
            kwargs["choices"] = kwargs.get("choices", MARKUP_CHOICES)
        super(MarkupField, self).__init__(*args, **kwargs)
    
    def formfield(self, **kwargs):
        if self.markup_default_filter:
            return None
        return super(MarkupField, self).formfield(**kwargs)
