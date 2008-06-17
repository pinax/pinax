from django import template
from django.conf import settings
from django.core.cache import cache
from os.path import abspath
from os.path import dirname as dn
from django.utils.version import get_svn_revision
register = template.Library()


@register.simple_tag
def svn_app_version(appname=None):
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
                module = __import__(appname,{},{},[''])
            except:
                if settings.DEBUG:
                    raise
                version = 'SVN-Error'
            else:
                version = get_svn_revision(dn(abspath(module.__file__)))
        cache.set(cname, version, 60*60*24*30)
    return version
