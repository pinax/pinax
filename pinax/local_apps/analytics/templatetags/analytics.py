from django import template
from django.conf import settings

register = template.Library()

def urchin():
    urchin_id = getattr(settings, 'URCHIN_ID', None)
    if urchin_id:
        return """
    <script src="http://www.google-analytics.com/urchin.js" type="text/javascript"></script>
    <script type="text/javascript">
        _uacct = "%s";
        urchinTracker();
    </script>
    """ % settings.URCHIN_ID
    else:
        return ""

register.simple_tag(urchin)