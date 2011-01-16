import re

from django.conf import settings



MASK_IN_EXCEPTION_EMAIL= ["password", "mail", "protected", "private"]
mask_re = re.compile("(" + "|".join(MASK_IN_EXCEPTION_EMAIL) + ")", re.I)



class HideSensistiveFieldsMiddleware(object):
    """
    A middleware that masks sensitive fields when an exception occurs,
    e.g. passwords in login attempts.
    """
    
    def process_exception(self, request, exception):
        if not request or not request.POST or settings.DEBUG:
            return None
        masked = False
        mutable = True
        if hasattr(request.POST, "_mutable"):
            mutable = request.POST._mutable
            request.POST._mutable = True
        for name in request.POST:
            if mask_re.search(name):
                request.POST[name] = u"xxHIDDENxx"
                masked = True
        if hasattr(request.POST, "_mutable"):
            request.POST._mutable = mutable
