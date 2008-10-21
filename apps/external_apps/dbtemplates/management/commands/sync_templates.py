import os
import re
from optparse import make_option

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.management.base import CommandError, NoArgsCommand
from django.template.loaders.app_directories import app_template_dirs

from dbtemplates.models import Template

class Command(NoArgsCommand):
    help = "Syncs file system templates with the database bidirectionally."
    option_list = NoArgsCommand.option_list + (
        make_option("-e", "--ext", dest="ext", action="store", default="html",
            help="extension of the files you want to sync with the database "
                 "[default: %default]"),
        make_option("-f", "--force", action="store_true", dest="force",
            default=False, help="overwrite existing database templates")
    )
    def handle_noargs(self, **options):
        extension = options.get('ext')
        force = options.get('force')

        if not extension.startswith("."):
            extension = ".%s" % extension

        try:
            site = Site.objects.get_current()
        except:
            site = None

        if site is None:
            raise CommandError("Please make sure to have the sites contrib "
                               "app installed and setup with a site object")

        if not type(settings.TEMPLATE_DIRS) in (tuple, list):
            raise CommandError("Please make sure settings.TEMPLATE_DIRS is a "
                               "list or tuple.")

        templatedirs = [d for d in
            settings.TEMPLATE_DIRS + app_template_dirs if os.path.isdir(d)]

        for templatedir in templatedirs:
            for dirpath, subdirs, filenames in os.walk(templatedir):
                for f in [f for f in filenames if f.endswith(extension)
                    and not f.startswith(".")]:
                    path = os.path.join(dirpath, f)
                    name = path.split(templatedir)[1][1:]
                    try:
                        t = Template.objects.get(name__exact=name)
                    except Template.DoesNotExist:
                        if force == False:
                            confirm = raw_input(
                                "\nA '%s' template doesn't exist in the database.\n"
                                "Create it with '%s'?"
                                    " (y/[n]): """ % (name, path))
                        if confirm.lower().startswith('y') or force:
                            t = Template(name=name,
                                content=open(path, "r").read())
                            t.save()
                            t.sites.add(site)
                    else:
                        while 1:
                            confirm = raw_input(
                                "\n%s exists in the database.\n"
                                "(1) Overwrite %s with '%s'\n"
                                "(2) Overwrite '%s' with %s\n"
                                "Type 1 or 2 or press <Enter> to skip: "
                                    % (t.__repr__(),
                                        t.__repr__(), path,
                                        path, t.__repr__()))
                            if confirm == '' or confirm in ('1', '2'):
                                if confirm == '1':
                                    t.content = open(path, 'r').read()
                                    t.save()
                                    t.sites.add(site)
                                elif confirm == '2':
                                    open(path, 'w').write(t.content)
                                break
