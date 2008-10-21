"""plugins template tag root hooks.
"""
from django.conf import settings
from django.db.models.loading import get_app
from django import template
from inspect import getargspec
from django.template.context import Context
from django.utils.functional import curry
from django.utils.encoding import smart_str
from django.template import loader, VariableDoesNotExist, Variable, Node
from django.template import TemplateDoesNotExist, TemplateSyntaxError
from django.core.cache.backends.locmem import CacheClass as LocalMemCache

TAG_KEYWORD_ARGUMENT_SEPARATOR = '='

## RED_FLAG: this feels wrong...
#from app_plugins.models import PluginPoint, Plugin
#from app_plugins.models import is_valid_label, construct_template_path
models = get_app('app_plugins')

APP_PLUGINS_CACHE_PARAMS = getattr(settings, 'APP_PLUGINS_CACHE_PARAMS',
                                     {'cull_frequency': 4,
                                      'max_entries': 3000,
                                     'timeout': 60*60*24*3, # 3 days
                                     })

app_plugin_apps_with_templates = LocalMemCache('localhost',
                                               APP_PLUGINS_CACHE_PARAMS)

# at import cache the app names for indexing
app_names = []
for app in settings.INSTALLED_APPS:
    name = app.split('.')[-1]
    if name not in app_names:
        app_names.append(name)
app_names = tuple(app_names)

def callback(func, variables, context, takes_context):
    """
    resolve an iterable of Variable objects into a list of args and a dict
    of keyword arguments. support full python style keyword argument
    processing::
        >>> def foo(a, b, c=1, d=2):
        ...     pass
        >>> foo(1, 2)
        >>> foo(1, b=2)
        >>> foo(b=2, a=1, d=3)
    """
    name = getattr(func, "_decorated_function", func).__name__
    params, varargs, varkw, defaults = getargspec(func)
    if takes_context:
        if params[0] == 'context':
            params.pop(0)
        else:
            raise TemplateSyntaxError(
                "Any tag function decorated with takes_context=True "
                "must have a first argument of 'context'")
    num_defaults = len(defaults)
    num_params = len(params)
    num_req = num_params - num_defaults

    args = []
    kwdargs = {}
    found_kwd = False
    for variable in variables:
        if not found_kwd:
            try:
                args.append(variable.resolve(context))
            except VariableDoesNotExist:
                if variable.var.count(TAG_KEYWORD_ARGUMENT_SEPARATOR) != 1:
                    raise
                found_kwd = True
        if found_kwd:
            try:
                var, path = variable.var.split(TAG_KEYWORD_ARGUMENT_SEPARATOR)
            except ValueError:
                raise TemplateSyntaxError(
                    "Expected keyword assignemnt, found '%s' instead" %
                    variable.var)
            if params and not varkw and name not in params:
                raise TemplateSyntaxError(
                    "%s got an unexpected keyword argument '%s'" % (name, var))
            if var in kwdargs:
                raise TemplateSyntaxError(
                    "%s got multiple values for keyword argument '%s'" %
                    (name, var))
            kwdargs[smart_str(var)] = Variable(path).resolve(context)

    num_args = len(args)
    num_kwds = len(kwdargs)
    num_all = num_args + num_kwds

    if ((num_args > num_params and not varargs) or
        (num_all> num_params and not varkw)):
        raise TemplateSyntaxError(
                "%s takes at most %s arguments. (%s given)" % (
                    name, num_params, num_all) )
    if num_args != num_req:
        if num_args > num_req:
            # some args are kwd args (maybe multiple keyword error)
            if not varargs:
                allowed = set(params[num_args:])
                not_allowed = set(kwdargs) - allowed
                if not_allowed:
                    raise TemplateSyntaxError(
                        "%s got multiple values for keyword arguments: %s" % (
                            name, ", ".join(not_allowed) ))
        elif not varkw:
            # not enough required parameters error
            required = set(params[num_args:-num_default])
            missing = required - set(kwdargs)
            if missing:
                raise TemplateSyntaxError(
                    "%s takes at least %s non-keyword arguments (%s given)" % (
                        name, num_req, num_args))
    if takes_context:
        args.insert(0, context)
    return func(*args, **kwdargs)

def compiler(node_class, parser, token):
    bits = token.split_contents()[1:]
    return node_class(bits)

def inclusion_kwdtag(register, file_name, context_class=Context,
                      takes_context=False):
        def dec(func):
            class InclusionKwdNode(Node):
                def __init__(self, vars_to_resolve):
                    self.vars_to_resolve = map(Variable, vars_to_resolve)

                def render(self, context):
                    new_context = callback(func, self.vars_to_resolve, context,
                                           takes_context)
                    if not getattr(self, 'nodelist', False):
                        if (not isinstance(file_name, basestring) and
                            is_iterable(file_name)):
                            t = loader.select_template(file_name)
                        else:
                            t = loader.get_template(file_name)
                        self.nodelist = t.nodelist
                    res = self.nodelist.render(context_class(new_context,
                            autoescape=context.autoescape))
                    context.pop() # local context
                    context.pop() # args
                    context.pop() # callback context (or empty)
                    return res

            compile_func = curry(compiler, InclusionKwdNode)
            compile_func.__doc__ = func.__doc__
            register.tag(getattr(func, "_decorated_function", func).__name__,
                         compile_func)
            return func
        return dec

register = template.Library()

@register.filter
def template_exists(templ):
    if templ is None: return False
    try:
        #loader.get_template(templ)
        loader.find_template_source(templ)
    except TemplateDoesNotExist:
        return False
    return True

def validate_name(name):
    ## red_flag: turn into a string
    if not models.is_valid_label(name):
        raise TemplateSyntaxError, "invalid plugin point name '%s'." % name

@inclusion_kwdtag(register, "app_plugins/app_plugin.html", takes_context=True)
def app_plugin(context, app, name, plugin=None, user=None, args=None,
               ext='.html', **extra_args):
    validate_name(app)
    validate_name(name)
    if plugin is None:
        try:
            plugin = models.Plugin.objects.get(label=u'.'.join([app, name]))
        except models.Plugin.DoesNotExist:
            pass
    nc = context

    if args is None: args = extra_args
    else: args.update(extra_args)

    template = ''
    if plugin is None:
        template = models.construct_template_path(app, name, ext)
        nc.push()
    else:
        nc.update(plugin.call(nc, user, **args))
        template = plugin.template
    nc.update(args)
    nc.push()
    nc['app_plugin'] = plugin
    nc['app_plugin_app'] = app
    nc['app_plugin_point'] = name
    nc['app_plugin_args'] = args
    nc['app_plugin_user'] = user
    nc['app_plugin_template'] = template
    return nc

@inclusion_kwdtag(register, "app_plugins/plugin_point.html", takes_context=True)
def plugin_point(context, name, point=None, user=None, ext='.html', **args):
    validate_name(name)
    if point is None:
        try:
            point = models.PluginPoint.objects.select_related().get(label=name)
        except models.PluginPoint.DoesNotExist:
            pass
    nc = context
    plugins = None
    if point is None:
        apps = app_plugin_apps_with_templates.get(name+ext, None)
        if apps is None:
            tpls = ((app, models.construct_template_path(app, name, ext))
                    for app in app_names)
            apps = [ app for app, tpl in tpls if template_exists(tpl) ]
            app_plugin_apps_with_templates.set(name+ext, apps)
        nc.push()
    else:
        nc.update(point.call(nc, user, **args))
        plugins = point.get_plugins(user)
        apps = [ p.app for p in plugins ]
    nc.update(args)
    nc.push()
    nc['app_plugin_ext'] = ext
    nc['app_plugin_point'] = name
    nc['app_plugin_apps'] = apps
    nc['app_plugin_args'] = args
    nc['app_plugin_user'] = user
    nc['app_plugin_plugins'] = plugins
    return nc
