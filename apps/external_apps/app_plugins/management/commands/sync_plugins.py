"""Load up the registered plugins and plugin points.

New model instances will be created for registered poings and plugins.
Any unregistered plugins for a registered point will have an instance created.
Any unregistered points for a registered plugin will have an instance created.

Registered plugins and points which are no longer in the library system
are marked unregistered and un-enabled.


FUTURE:
    We could try to do a file system search for all unregistered plugins and
determine the connected points, but we would not be able to find db plugins
easily or those provided by more custom loaders. At some future point we may
consider having a loader extension API for listing unregistered plugins.

"""
from django.conf import settings
from django.template import loader, TemplateDoesNotExist
#from library import libraries
#from models import Plugin, PluginPoint, REMOVED, ENABLED
#from models import construct_template_path

from django.core.management.base import NoArgsCommand
from optparse import make_option

class Command(NoArgsCommand):
    option_list = NoArgsCommand.option_list + (
        make_option('--delete', action='store_true', dest='delete',
            help='delete the REMOVED Plugin and PluginPoint instances. '),
    )
    help = ("Syncs the registered plugin and plugin points with the model "
            "versions.")

    requires_model_validation = True

    def handle_noargs(self, **options):
        sync_app_plugins(options.get('delete', False))

def sync_app_plugins(delete_removed=False):
    """
    We need to do a complicated dance to sync the current registered and
    unregistered implicit plugins and points with the instances in the DB.
    Plugins and points which are removed (or can no longer be found) are
    marked REMOVED (sometimes only to be re-enabed shortly there after).
    There is the option to delete all entries which are marked removed, but
    this should be done carefully. Other apps may have relations to the
    plugins and points for user preferences and customizaiton settings.
    We do not want to blindly delete these in a chain delete, as they may need
    to be migrated to a renamed plugin or point which has now been created as
    part of the sync.

    The process:
        1. for each registered Plugin Point
        1.1. if no instance exists, create it enabled.
        1.2. mark it registered
        1.2. if it was 'removed' then mark it enabled
        2. For each non-removed, registered instance for which there was no reg
        2.1. mark removed
        2.2. mark plugins removed
        3. for each registered plugin
        3.1. if there is no point, create it as unregistered
        3.2. if there is no plugin, create it as reg and enabled, w/template
        3.3. test the template load
        3.4. if the plugin was marked REMOVED
        3.4.1. mark it enabled
        3.4.2. if its point is REMOVED and it is not marked reg, enable it
        4. for each registered plugin for which there is no registration
        4.1. mark it removed
        5. for each non-REMOVED point, get all unregistered plugins via load:
        5.1. if plugin instance does not exist, create unregistered and enable
        5.2. if it does exist and is marked REMOVED, mark unreg-enabled w/ point
        6. for each unreg-non-removed point
        6.1. if all plugins are REMOVED, mark REMOVED.
        7. if asked to delete the removed, do so.
    """
    from app_plugins.library import libraries
    from app_plugins.models import Plugin, PluginPoint, REMOVED, ENABLED
    from app_plugins.models import construct_template_path

    instances = dict((p.label, p) for p in PluginPoint.objects.all())

    ## section 1 - registered plugin points
    for app_label, lib in libraries.iteritems():
        for label in lib.plugin_points:
            pp = instances.pop(label, None)
            if pp is None:
                print "Creating registered PluginPoint:", label
                pp = PluginPoint(label=label)
            pp.registered = True
            if pp.status == REMOVED:
                print "Updating registered PluginPoint:", label
                # re-enable a previously removed plugin point and its plugins
                pp.status = ENABLED
                for p in Plugin.objects.filter(point=pp, status=REMOVED):
                    p.status = ENABLED
                    p.save()
            pp.save()
            # search for unregistered plugins we do not yet know about?

    ## section 2 - removed plugin points
    for pp in instances.itervalues():
        if pp.status != REMOVED:
            pp.status = REMOVED
            pp.save()
            for p in pp.plugin_set.all():
                p.status = REMOVED
                p.save()

    instances = dict((p.label, p) for p in Plugin.objects.all())

    ## section 3 - registered plugins
    for app_label, lib in libraries.iteritems():
        for label in lib.plugins:
            p = instances.pop(label, None)
            point_label = label[len(lib.app_name):]
            if p is None:
                p = Plugin()
                p.label = label
                print "Creating registered Plugin:", label
                try:
                    point = PluginPoint.objects.get(label=point_label)
                    p.point = point
                    if point.status == REMOVED:
                        # point was removed at some point...
                        point.status = ENABLED
                        if point.registered:
                            point.registered = False
                        point.save()
                except PluginPoint.DoesNotExist:
                    print "Creating unregistered PluginPoint:", point_label
                    point = PluginPoint(label=point_label)
                    point.save()
                    p.point = point
            p.registered = True
            if p.status == REMOVED:
                # re-enable a previously removed plugin
                print "Updating registered Plugin:", p.label
                p.status = ENABLED
            options = lib.get_plugin_call(point_label).options
            default = construct_template_path(lib.app_name, point_label,
                                              options.get('ext', '.html'))
            # raise an error if it does not exist...
            template = options.get('template', default)
            loader.find_template_source(template)
            p.template = template
            p.save()

    ## section 4 - initial marking of unregistered known plugins
    for p in instances.itervalues():
        if p.status != REMOVED:
            p.status = REMOVED
            p.save()

    ## section 5 - unregistered plugins
    instances = dict((p.label, p) for p in Plugin.objects.all())
    for pp in PluginPoint.objects.exclude(status=REMOVED):
        ext = pp.get_options().get('ext', '.html')
        name = pp.label
        for app in settings.INSTALLED_APPS:
            label = u'.'.join([app, name])
            template = construct_template_path(app, name, ext)
            bFound = True
            try:
                loader.find_template_source(template)
            except TemplateDoesNotExist:
                bFound = False
            p = instances.get(label, None)
            if p is None:
                if bFound:
                    print "Creating unregistered Plugin:", label
                    p = Plugin(point=pp, label=label, template=template)
            else:
                if p.status == REMOVED and bFound:
                    p.status = ENABLED
                    p.template = template
                    p.registered = False
                    #print "Updating unregistered Plugin:", label
                elif not p.registered and not bFound and p.status != REMOVED:
                    p.status = REMOVED
                else:
                    p = None
            if p is not None:
                p.save()

    ## section 6 - removed unregistered plugin points
    for pp in PluginPoint.objects.filter(registered=False).exclude(status=REMOVED):
        if not pp.plugin_set.exclude(status=REMOVED).count():
            print "Removing unregistered PluginPoint:", pp.label
            pp.status = REMOVED
            pp.save()

    ## section 7 - delete removed
    if delete_removed:
        count = Plugin.objects.filter(status=REMOVED).count()
        if count:
            print "Deleting %d Removed Plugins" % count
            Plugin.objects.filter(status=REMOVED).delete()
        count = PluginPoints.objects.filter(status=REMOVED).count()
        if count:
            print "Deleting %d Removed PluginPoint" % count
            PluginPoints.objects.filter(status=REMOVED).delete()
