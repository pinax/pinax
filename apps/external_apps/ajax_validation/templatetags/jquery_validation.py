import os

from django import template

import ajax_validation

register = template.Library()

VALIDATION_SCRIPT = open(os.path.join(os.path.dirname(ajax_validation.__file__), 'static', 'js', 'jquery-ajax-validation.js')).read()

def include_validation():
    return '''<script type="text/javascript">%s</script>''' % VALIDATION_SCRIPT
register.simple_tag(include_validation)
