from django import template
from django.conf import settings

from config import config


register = template.Library()


@register.simple_tag
def analytics():
    content = ""
    for kind, codes in config.get("ANALYTICS_SETTINGS", {}).items():
        code = codes.get(str(settings.SITE_ID))
        if code is not None:
            t = template.loader.get_template("analytics/_%s.html" % kind)
            content += t.render(template.Context({
                "code": code
            }))
    return content
