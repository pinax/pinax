from django.utils.functional import Promise
from django.utils.encoding import force_unicode
from simplejson import JSONEncoder

class LazyEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Promise):
            return force_unicode(obj)
        return obj
