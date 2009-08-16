import os
import sys
import glob
import shutil
from optparse import make_option

from django.conf import settings
from django.db.models import get_apps
from django.utils.text import get_text_list
from django.core.management.base import BaseCommand, CommandError, AppCommand

from staticfiles.utils import import_module

try:
    set
except NameError:
    from sets import Set as set # Python 2.3 fallback

MEDIA_DIRNAMES = getattr(settings, 'STATICFILES_MEDIA_DIRNAMES', ['media'])
EXTRA_MEDIA = getattr(settings, 'STATICFILES_EXTRA_MEDIA', ())
PREPEND_LABEL_APPS = getattr(
    settings, 'STATICFILES_PREPEND_LABEL_APPS', ('django.contrib.admin',))

class Command(AppCommand):
    """
    Command that allows to copy or symlink media files from different
    locations to the settings.MEDIA_ROOT.

    Based on the collectmedia management command by Brian Beck:
    http://blog.brianbeck.com/post/50940622/collectmedia
    """
    media_files = {}
    media_dirs = MEDIA_DIRNAMES
    media_root = settings.MEDIA_ROOT
    exclude = ['CVS', '.*', '*~']
    option_list = AppCommand.option_list + (
        make_option('-i', '--interactive', action='store_true', dest='interactive',
            help="Run in interactive mode, asking before modifying files and selecting from multiple sources."),
        make_option('-a', '--all', action='store_true', dest='all',
            help="Traverse all installed apps."),
        make_option('--media-root', default=media_root, dest='media_root', metavar='DIR',
            help="Specifies the root directory in which to collect media files."),
        make_option('-m', '--media-dir', action='append', default=media_dirs, dest='media_dirs', metavar='DIR',
            help="Specifies the name of the media directory to look for in each app."),
        make_option('-e', '--exclude', action='append', default=exclude, dest='exclude', metavar='PATTERNS',
            help="A space-delimited list of glob-style patterns to ignore. Use multiple times to add more."),
        make_option('-n', '--dry-run', action='store_true', dest='dry_run',
            help="Do everything except modify the filesystem."),
        make_option('-l', '--link', action='store_true', dest='link',
            help="Create a symbolic link to each file instead of copying."),
    )
    help = 'Collect media files of apps, Pinax and the project in a single media directory.'
    args = '[appname appname ...]'

    def handle(self, *app_labels, **options):
        media_root = os.path.normpath(
            options.get('media_root', settings.MEDIA_ROOT))

        if not os.path.isdir(media_root):
            raise CommandError(
                'Designated media location %s could not be found.' % media_root)

        if options.get('dry_run', False):
            print "\n    DRY RUN! NO FILES WILL BE MODIFIED."
        print "\nCollecting media in %s" % media_root

        if app_labels:
            try:
                app_list = [models.get_app(label) for label in app_labels]
            except (ImproperlyConfigured, ImportError), e:
                raise CommandError(
                    "%s. Is your INSTALLED_APPS setting correct?" % e)
        else:
            if not options.get('all', False):
                raise CommandError('Enter at least one appname or use the --all option')

            app_list = []
            for app_entry in settings.INSTALLED_APPS:
                try:
                    app_mod = import_module(app_entry)
                except ImportError, e:
                    raise CommandError('ImportError %s: %s' % (app, e.args[0]))
                app_media_dir = os.path.join(
                    os.path.dirname(app_mod.__file__), 'media')
                if os.path.isdir(app_media_dir):
                    app_list.append(app_mod)

        app_labels = [app.__name__.rsplit('.', 1)[-1] for app in app_list]
        print "Traversing apps: %s" % get_text_list(app_labels, 'and')
        for app_mod in app_list:
            self.handle_app(app_mod, **options)

        # Look in additional locations for media
        extra_media = []
        for label, path in EXTRA_MEDIA:
            if os.path.isdir(path):
                extra_media.append((label, path))
        extra_labels = [label for label, path in extra_media]
        print "Looking additionally in: %s" % get_text_list(extra_labels, 'and')
        exclude = options.get('exclude')
        for extra_label, extra_path in extra_media:
            self.add_media_files(extra_label, extra_path, exclude)

        # This mapping collects files that may be copied.  Keys are what the
        # file's path relative to `media_root` will be when copied.  Values
        # are a list of 2-tuples containing the the name of the app providing
        # the file and the file's absolute path.  The list will have a length
        # greater than 1 if multiple apps provide a media file with the same
        # relative path.

        # Forget the unused versions of a media file
        for f in self.media_files:
            self.media_files[f] = dict(self.media_files[f]).items()

        # Stop if no media files were found
        if not self.media_files:
            print "\nNo media found."
            return

        interactive = options.get('interactive', False)
        # Try to copy in some predictable order.
        destinations = list(self.media_files)
        destinations.sort()
        for destination in destinations:
            sources = self.media_files[destination]
            first_source, other_sources = sources[0], sources[1:]
            if interactive and other_sources:
                first_app = first_source[0]
                app_sources = dict(sources)
                for (app, source) in sources:
                    if destination.startswith(app):
                        first_app = app
                        first_source = (app, source)
                        break
                print "\nThe file %r is provided by multiple apps:" % destination
                print "\n".join(["    %s" % app for (app, source) in sources])
                message = "Enter the app that should provide this file [%s]: " % first_app
                while True:
                    app = raw_input(message)
                    if not app:
                        app, source = first_source
                        break
                    elif app in app_sources:
                        source = app_sources[app]
                        break
                    else:
                        print "The app %r does not provide this file." % app
            else:
                app, source = first_source

            # Special case apps that have media in <app>/media, not in
            # <app>/media/<app>, e.g. django.contrib.admin
            if app in [app.rsplit('.', 1)[-1] for app in PREPEND_LABEL_APPS]:
                destination = os.path.join(app, destination)

            print "\nSelected %r provided by %r." % (destination, app)
            self.process_file(source, destination, media_root, **options)

    def handle_app(self, app, **options):
        exclude = options.get('exclude')
        media_dirs = options.get('media_dirs')
        app_label = app.__name__.rsplit('.', 1)[-1]
        app_root = os.path.dirname(app.__file__)
        for media_dir in media_dirs:
            app_media = os.path.join(app_root, media_dir)
            if os.path.isdir(app_media):
                self.add_media_files(app_label, app_media, exclude)

    def add_media_files(self, app, location, exclude):
        prefix_length = len(location) + len(os.sep)
        for root, dirs, files in os.walk(location):
            # Filter files based on the exclusion pattern.
            for filename in self.filter_names(files, exclude=exclude):
                absolute_path = os.path.join(root, filename)
                relative_path = absolute_path[prefix_length:]
                self.media_files.setdefault(
                    relative_path, []).append((app, absolute_path))

    def process_file(self, source, destination, root, link=False, **options):
        dry_run = options.get('dry_run', False)
        interactive = options.get('interactive', False)
        destination = os.path.abspath(os.path.join(root, destination))
        if not dry_run:
            # Get permission bits and ownership of `root`.
            try:
                root_stat = os.stat(root)
            except os.error, e:
                mode = 0777 # Default for `os.makedirs` anyway.
                uid = gid = None
            else:
                mode = root_stat.st_mode
                uid, gid = root_stat.st_uid, root_stat.st_gid
            destination_dir = os.path.dirname(destination)
            try:
                # Recursively create all the required directories, attempting
                # to use the same mode as `root`.
                os.makedirs(destination_dir, mode)
            except os.error, e:
                # This probably just means the leaf directory already exists,
                # but if not, we'll find out when copying or linking anyway.
                pass
            else:
                if None not in (uid, gid):
                    os.lchown(destination_dir, uid, gid)
        if link:
            success = self.link_file(source, destination, interactive, dry_run)
        else:
            success = self.copy_file(source, destination, interactive, dry_run)
        if success and None not in (uid, gid):
            # Try to use the same ownership as `root`.
            os.lchown(destination, uid, gid)

    def copy_file(self, source, destination, interactive=False, dry_run=False):
        "Attempt to copy `source` to `destination` and return True if successful."
        if interactive:
            exists = os.path.exists(destination) or os.path.islink(destination)
            if exists:
                print "The file %r already exists." % destination
                if not self.prompt_overwrite(destination):
                    return False
        print "Copying %r to %r." % (source, destination)
        if not dry_run:
            try:
                os.remove(destination)
            except os.error, e:
                pass
            shutil.copy2(source, destination)
            return True
        return False

    def link_file(self, source, destination, interactive=False, dry_run=False):
        "Attempt to link to `source` from `destination` and return True if successful."
        if sys.platform == 'win32':
            message = "Linking is not supported by this platform (%s)."
            raise os.error(message % sys.platform)
        
        if interactive:
            exists = os.path.exists(destination) or os.path.islink(destination)
            if exists:
                print "The file %r already exists." % destination
                if not self.prompt_overwrite(destination):
                    return False
        if not dry_run:
            try:
                os.remove(destination)
            except os.error, e:
                pass
        print "Linking to %r from %r." % (source, destination)
        if not dry_run:
            os.symlink(source, destination)
            return True
        return False

    def prompt_overwrite(self, filename, default=True):
        "Prompt the user to overwrite and return their selection as True or False."
        yes_values = ['Y']
        no_values = ['N']
        if default:
            prompt = "Overwrite? [Y/n]: "
            yes_values.append('')
        else:
            prompt = "Overwrite? [y/N]: "
            no_values.append('')
        while True:
            overwrite = raw_input(prompt).strip().upper()
            if overwrite in yes_values:
                return True
            elif overwrite in no_values:
                return False
            else:
                print "Select 'Y' or 'N'."

    def filter_names(self, names, exclude=None, func=glob.fnmatch.filter):
        if exclude is None:
            exclude = []
        elif isinstance(exclude, basestring):
            exclude = exclude.split()
        else:
            exclude = [pattern for patterns in exclude for pattern in patterns.split()]
        excluded_names = set(
            [name for pattern in exclude for name in func(names, pattern)])
        return set(names) - excluded_names
