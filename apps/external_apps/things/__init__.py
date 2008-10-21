from things.options import *
from things.fields import *
from things.sites import ThingSite, site

# To placate PyFlakes
def __exported_functionality__():
    return [
        Thing, ModelThing, ThingGroup, OrderField, ForeignKeyAggregate,
        GenericForeignKeyAggregate, OrderSumField, OrderCountField,
        OrderGenericCountField, OrderGenericSumField, ThingSite, site,
        ASCENDING, DESCENDING
    ]

def autodiscover():
    """
    Auto-discover INSTALLED_APPS thing.py modules and fail silently when 
    not present. This forces an import on them to register any thing bits they
    may want.
    """
    import imp
    from django.conf import settings

    for app in settings.INSTALLED_APPS:
        # For each app, we need to look for an thing.py inside that app's
        # package. We can't use os.path here -- recall that modules may be
        # imported different ways (think zip files) -- so we need to get
        # the app's __path__ and look for thing.py on that path.

        # Step 1: find out the app's __path__ Import errors here will (and
        # should) bubble up, but a missing __path__ (which is legal, but weird)
        # fails silently -- apps that do weird things with __path__ might
        # need to roll their own thing registration.
        try:
            app_path = __import__(app, {}, {}, [app.split('.')[-1]]).__path__
        except AttributeError:
            continue

        # Step 2: use imp.find_module to find the app's thing.py. For some
        # reason imp.find_module raises ImportError if the app can't be found
        # but doesn't actually try to import the module. So skip this app if
        # its thing.py doesn't exist
        try:
            imp.find_module('thing', app_path)
        except ImportError:
            continue

        # Step 3: import the app's thing file. If this has errors we want them
        # to bubble up.
        __import__("%s.thing" % app)