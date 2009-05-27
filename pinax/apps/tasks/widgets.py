from django import forms
from django.utils.html import escape, conditional_escape
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe

class ReadOnlyWidget(forms.TextInput):
    input_type = 'hidden'
    
    def __init__(self, field, *args, **kwargs):
        self.field = field
        super(ReadOnlyWidget, self).__init__(*args, **kwargs)
    
    def render(self, *args, **kwargs):
        field_name, value = args
        field_type = self.field.__class__.__name__
        field_value = super(ReadOnlyWidget, self).render(*args, **kwargs)
        output = value
        
        try:
            if self.field.choices:
                for choice in self.field.choices:
                    if value == choice[0]:
                        output = conditional_escape(force_unicode(choice[1]))
            else:
                    output = escape(value)
        except Exception,e:
            output = e
        
        return mark_safe('<span>%s</span>\n%s' % (output, field_value))
    