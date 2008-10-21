import os
from django.conf import settings
from django.db.models import signals
from django.template import TemplateDoesNotExist
from django.contrib.sites.models import Site

from dbtemplates.models import Template

try:
    site = Site.objects.get_current()
except:
    site = None

try:
    cache_dir = os.path.normpath(getattr(settings, 'DBTEMPLATES_CACHE_DIR', None))
    if not os.path.isdir(cache_dir):
        raise
except:
    cache_dir = None
    
def load_template_source(template_name, template_dirs=None):
    """
    Tries to load the template from DBTEMPLATES_CACHE_DIR. If it does not exist 
    loads templates from the database by querying the database field ``name``
    with a template path and ``sites`` with the current site,
    and tries to save the template as DBTEMPLATES_CACHE_DIR/``name`` for subsequent
    requests.
    If DBTEMPLATES_CACHE_DIR is not configured falls back to database-only operation.
    """
    if site is not None:
        if cache_dir is not None:
            filepath = os.path.join(cache_dir, template_name)
            try:
                return (open(filepath).read(), filepath)
            except IOError:
                try:
                    t = Template.objects.get(name__exact=template_name, sites__pk=site.id)
                    try:
                        f = open(filepath, 'w')
                        f.write(t.content)
                        f.close()
                    except IOError:
                            try:
                                head, tail = os.path.split(filepath)
                                if head and not os.path.isdir(head):
                                    os.makedirs(head)
                            except Exception:
                                pass
                            
                    return (t.content, 'db:%s:%s' % (settings.DATABASE_ENGINE, template_name))
                except:
                    pass
        else:
            try:
                t = Template.objects.get(name__exact=template_name, sites__pk=site.id)
                return (t.content, 'db:%s:%s' % (settings.DATABASE_ENGINE, template_name))
            except:
                pass
    raise TemplateDoesNotExist, template_name
load_template_source.is_usable = True

def remove_cached_template(instance, **kwargs):
    """
    Called via django's signals to remove cached templates, if the template in the
    database was changed or deleted.
    """
    if cache_dir is not None:
        try:
            filepath = os.path.join(cache_dir, instance.name)
            os.remove(filepath)
        except OSError:
            pass

signals.post_save.connect(remove_cached_template, sender=Template)
signals.pre_delete.connect(remove_cached_template, sender=Template)
