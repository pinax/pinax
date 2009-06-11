import glob
import os
import optparse
import sys
import shutil
import re
import random
import pinax

from optparse import make_option
from django.core.management.base import BaseCommand

EXCLUDED_PATTERNS = ('.svn',)
DEFAULT_PINAX_ROOT = None # fallback to the normal PINAX_ROOT in settings.py.
PINAX_ROOT_RE = re.compile(r'PINAX_ROOT\s*=.*$', re.M)
SECRET_KEY_RE = re.compile(r'SECRET_KEY\s*=.*$', re.M)
ROOT_URLCONF_RE = re.compile(r'ROOT_URLCONF\s*=.*$', re.M)
VIRTUALENV_BASE_RE = re.compile(r'VIRTUALENV_BASE\s*=.*$', re.M)
CHARS = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'

def get_pinax_root(default_pinax_root):
    if default_pinax_root is None:
        return os.path.abspath(os.path.dirname(pinax.__file__))
    return default_pinax_root


def get_projects_dir(pinax_root):
    return os.path.join(pinax_root, 'projects')


def get_projects(pinax_root):
    projects = []
    for item in glob.glob(os.path.join(get_projects_dir(pinax_root), '*')):
        if os.path.isdir(item):
            projects.append(item)
    return projects


def copytree(src, dst, symlinks=False):
    """
    Backported from the Python 2.6 source tree, then modified for this script's
    purposes.
    """
    names = os.listdir(src)

    os.makedirs(dst)
    errors = []
    for name in names:
        ignore = False
        for pattern in EXCLUDED_PATTERNS:
            if pattern in os.path.join(src, name):
                ignore = True
        if ignore:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks)
            else:
                shutil.copy2(srcname, dstname)
        except (IOError, os.error), why:
            errors.append((srcname, dstname, str(why)))
        except shutil.Error, err:
            errors.extend(err.args[0])
    try:
        shutil.copystat(src, dst)
    except OSError, why:
        if shutil.WindowsError is not None and isinstance(why,
            shutil.WindowsError):
            pass
        else:
            errors.extend((src, dst, str(why)))
    if errors:
        raise shutil.Error, errors


def update_settings(pinax_root, path, old_name, new_name):
    settings_file = open(path, 'r')
    settings = settings_file.read()
    settings_file.close()
    settings = settings.replace(old_name, new_name)
    if pinax_root is not None:
        settings = PINAX_ROOT_RE.sub("PINAX_ROOT = '%s'" % (pinax_root,),
            settings)
    new_secret_key = ''.join([random.choice(CHARS) for i in xrange(50)])
    settings = SECRET_KEY_RE.sub("SECRET_KEY = '%s'" % (new_secret_key,),
        settings)
    new_root_urlconf = '%s.urls' % new_name
    settings = ROOT_URLCONF_RE.sub("ROOT_URLCONF = '%s'" % new_root_urlconf,
        settings)
    settings_file = open(path, 'w')
    settings_file.write(settings)
    settings_file.close()


def update_rename_deploy_files(path, old_name, new_name):
    for deploy_file in glob.glob(os.path.join(path, "pinax") + '*'):
        df = open(deploy_file, 'r')
        deploy_settings = df.read()
        df.close()
        deploy_settings = deploy_settings.replace(old_name, new_name)
        df = open(deploy_file, 'w')
        df.write(deploy_settings)
        df.close()
        deploy_filepath = os.path.dirname(deploy_file)
        deploy_filename = os.path.basename(deploy_file)
        new_deploy_file = os.path.join(deploy_filepath, deploy_filename.replace("pinax", new_name))
        shutil.move(deploy_file, new_deploy_file)
    # fix modpython.py
    modpython_file = open(os.path.join(path, "modpython.py"), "rb")
    modpython = modpython_file.read()
    modpython_file.close()
    virtualenv_base = os.environ.get("VIRTUAL_ENV", "")
    modpython = VIRTUALENV_BASE_RE.sub('VIRTUALENV_BASE = "%s"' % virtualenv_base, modpython)
    modpython_file = open(os.path.join(path, "modpython.py"), "wb")
    modpython_file.write(modpython)
    modpython_file.close()


def main(default_pinax_root, project_name, destination, verbose=True):
    if os.path.exists(destination):
        print "Files already exist at this path: %s" % (destination,)
        sys.exit(1)
    user_project_name = os.path.basename(destination)
    pinax_root = get_pinax_root(default_pinax_root)
    if project_name in map(os.path.basename, get_projects(pinax_root)):
        source = os.path.join(get_projects_dir(pinax_root), project_name)
    else:
        if not os.path.exists(project_name):
            print "Project template does not exist at this path: %s" % (
                project_name,)
            sys.exit(1)
        source = project_name
    if verbose:
        print "Copying your project to its new location"
    copytree(source, destination)
    if verbose:
        print "Updating settings.py for your new project"
    update_settings(default_pinax_root, os.path.join(destination, 'settings.py'),
        project_name, user_project_name)
    if verbose:
        print "Renaming and updating your deployment files"
    update_rename_deploy_files(os.path.join(destination, 'deploy'), project_name,
        user_project_name)
    if verbose:
        print "Finished cloning your project, now you may enjoy Pinax!"


class Command(BaseCommand):
    help = "Clones a Pinax starter project to <new_project_name> (which can be a path)."
    args = "<original_project> <new_project_name>"
        
    clone_project_options = (
        make_option('-l', '--list-projects', dest='list_projects',
            action = 'store_true',
            help = 'lists the projects that are available on this system'),
        make_option('-r', '--pinax-root', dest='pinax_root',
            default = DEFAULT_PINAX_ROOT,
            action = 'store_true',
            help = 'where Pinax lives on your system (defaults to Pinax in your virtual environment)'),
        make_option('-b', '--verbose', dest='verbose',
            action = 'store_false', default=True,
            help = 'enables verbose output'),
    )
        
    option_list = BaseCommand.option_list + clone_project_options
    
    
    def handle(self, *args, **options):
        """
        Handle clone_project options and run main to perform clone_project
        operations.
        """
        
        if options.get('list_projects'):
            pinax_root = get_pinax_root(options.get('pinax_root'))
            print "Available Projects"
            print "------------------"
            sys.path.insert(0, get_projects_dir(pinax_root))
            for project in map(os.path.basename, get_projects(pinax_root)):
                print "%s:" % project
                about = getattr(__import__(project), '__about__', '')
                for line in about.strip().splitlines():
                    print '    %s' % line
                print
            sys.exit(0)

        main(options.get('pinax_root'), args[0], args[1],
            verbose = options.get('verbose')
        )
        return 0
        