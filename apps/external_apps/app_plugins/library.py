from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import curry
from django.utils.datastructures import SortedDict

libraries = {}

def _register(lib, store, prefix, options, do_error, call):
    'generic module library registration decorator passthrough'
    if call is None:
        if do_error:
            raise RuntimeError, "No callable recieved."
        return curry(_register, lib, store, prefix, options, True)
    if not callable(call):
        raise SyntaxError, "must supply callable"
    if not hasattr(call, '__module__'):
        raise SyntaxError, "callable must have __module__ defined"
    if not hasattr(call, '__name__'):
        raise SyntaxError, "callable must have __name__ defined"
    name = call.__name__
    if prefix: name = prefix + '.' + call.__name__
    if name in store:
        raise RuntimeError, "library already has a call for " + name
    if lib.app_name is None:
        lib.app_name = call.__module__
        libraries[lib.app_name] = lib
    elif lib.app_name != call.__module__:
        raise RuntimeError, ("library is for module %s, not %s." %
                             (lib.app_name, call.__module__))
    store[name] = call
    call.options = options
    return call

class Library(object):
    def __init__(self):
        self.app_name = None
        self.point_calls = SortedDict()
        self.plugin_calls = SortedDict()

    @property
    def plugin_points(self):
        return ('.'.join([self.app_name, p]) for p in self.point_calls)

    @property
    def plugins(self):
        return ('.'.join([self.app_name, p]) for p in self.plugin_calls)

    def get_plugin_point_call(self, name):
        return self.point_calls[name]

    def get_plugin_call(self, name):
        return self.plugin_calls[name]

    def plugin_point(self, call=None, **options):
        return _register(self, self.point_calls, '', options, False, call)

    def plugin(self, call=None, **options):
        if not callable(call) and cal is not None:
            point_app = call
            call = None
        else:
            point_app = ''
        return _register(self, self.plugin_calls, point_app, options,
                         False, call)

def get_library(app):
    return libraries.get(app, None)
