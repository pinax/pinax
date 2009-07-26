from django import template
from django.conf import settings
from django.core.cache import cache
from django.utils.encoding import smart_str
from os.path import abspath
from os.path import dirname as dn
from django.utils.version import get_svn_revision
from django.db.models.loading import get_app
register = template.Library()


@register.simple_tag
def svn_app_version(appname=None, fail_silently=bool(not settings.DEBUG)):
    """
    foo.app {% svn_app_version "foo.app" %}
    project {% svn_app_version %}
    """
    cname = 'svn_app_version'
    if appname: cname += '.' + appname
    version = cache.get(cname)
    if not version:
        if not appname:
            ## RED_FLAG: hard coded relative root!
            version = get_svn_revision(dn(dn(dn(abspath(__file__)))))
        elif appname == 'django':
            version = get_svn_revision()
        elif appname not in settings.INSTALLED_APPS:
            version = 'SVN-None'
        else:
            try:
                module = get_app(appname)
            except:
                if not fail_silently: raise
                version = 'SVN-Error'
            else:
                version = get_svn_revision(dn(abspath(module.__file__)))
        cache.set(cname, version, 60*60*24*30)
    return version

def get_all_versions(fail_silently=bool(not settings.DEBUG)):
    # this cannot be done on load as there would be circular and parital imports
    try:
        allnames = ['', 'django'] + settings.INSTALLED_APPS
        res = [ (app, smart_str(svn_app_version(app, fail_silently)))
                    for app in allnames ]
    except:
        if fail_silently: return []
        raise
    return res
