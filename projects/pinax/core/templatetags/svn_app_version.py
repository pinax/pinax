from django import template
from django.conf import settings
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
    if not appname:
        ## RED_FLAG: hard coded relative root!
        return get_svn_revision(dn(dn(dn(abspath(__file__)))))

    if appname not in settings.INSTALLED_APPS: return 'SVN-None'
    try:
        module = __import__(app_name,{},{},[''])
    except:
        return 'SVN-Error'
    return get_svn_revision(dn(abspath(module.__file__))
