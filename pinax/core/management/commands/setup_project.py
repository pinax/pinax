import optparse
import os
import random
import re
import shutil
import sys

import pinax

from pinax.core.management.base import BaseCommand, CommandError



PROJECTS_DIR = os.path.join(os.path.dirname(pinax.__file__), "projects")



class Command(BaseCommand):
    
    help = "Creates a new Django project"
    args = "[projectname]"
    
    option_list = BaseCommand.option_list + [
        optparse.make_option("-l", "--list-bases",
            dest = "list_bases",
            action = "store_true",
            help = "lists the starter projects (bases) that are available"
        ),
        optparse.make_option("-b", "--base",
            dest = "base",
            default = "zero",
            help = "the starter project to use as a base (excluding _project, e.g., basic or social. see --list-projects)"
        )
    ]
    
    def handle(self, *args, **options):
        
        if options["list_bases"]:
            self.base_list()
            sys.exit(0)
        
        if not args:
            # note: --help prints full path to pinax-admin
            self.print_help("pinax-admin", "setup_project")
            sys.exit(0)
        
        self.setup_project(args[0], options["base"])
    
    def base_list(self):
        
        sys.path.append(PROJECTS_DIR)
        
        for project in self.project_list():
            print project.replace("_project", "")
            __about__ = getattr(__import__(project), "__about__", "")
            for line in __about__.strip().splitlines():
                print "    %s" % line
            print
        
        sys.path.pop()
    
    def project_list(self):
        
        projects = []
        
        for e in os.listdir(PROJECTS_DIR):
            if os.path.isdir(os.path.join(PROJECTS_DIR, e)):
                projects.append(e)
        
        return projects
    
    def setup_project(self, destination, base):
        
        user_project_name = os.path.basename(destination)
        
        if os.path.exists(destination):
            raise CommandError("Destination path already exists [%s]" % destination)
        
        try:
            # check to see if the project_name copies an existing module name
            __import__(user_project_name)
        except ImportError:
            # The module does not exist so we let Pinax create it as a project
            pass
        else:
            # The module exists so we raise a CommandError and exit
            raise CommandError(
                "'%s' conflicts with the name of an existing Python "
                "package/module and cannot be used as a project name. Please "
                "try another name." % project_name
            )
        
        # check the base value (we could later be much smarter about it and
        # allow repos and such)
        if base in [p.replace("_project", "") for p in self.project_list()]:
            project_name = "%s_project" % base
            source = os.path.join(PROJECTS_DIR, project_name)
        else:
            if not os.path.exists(base):
                raise CommandError(
                    "Project template does not exist the given "
                    "path: %s" % base
                )
            else:
                project_name = os.path.basename(base)
        
        copytree(source, destination,
            excluded_patterns=[
                ".svn", ".pyc", "dev.db"
            ]
        )
        
        ProjectFixer(destination, project_name, user_project_name).fix()


class ProjectFixer(object):
    """
    Fixes up a project to work correctly.
    """
    
    def __init__(self, project_dir, project_name, user_project_name):
        self.project_dir = project_dir
        self.project_name = project_name
        self.user_project_name = user_project_name
    
    def fix(self):
        self.fix_settings()
    
    def generate_secret_key(self):
        chars = "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)"
        return "".join([random.choice(chars) for i in xrange(50)])
    
    def fix_settings(self):
        # @@@ settings refactor
        settings_filename = os.path.join(self.project_dir, "settings.py")
        
        data = open(settings_filename, "rb").read()
        
        data = re.compile(r"SECRET_KEY\s*=.*$", re.M).sub(
            'SECRET_KEY = "%s"' % self.generate_secret_key(), data
        )
        data = re.compile(r"ROOT_URLCONF\s*=.*$", re.M).sub(
            'ROOT_URLCONF = "%s"' % "%s.urls" % self.user_project_name, data,
        )
        data = data.replace(self.project_name, self.user_project_name)
        
        open(settings_filename, "wb").write(data)


def copytree(src, dst, symlinks=False, excluded_patterns=None):
    """
    Modified copytree from Python 2.6 (backported to run on 2.4)
    """
    
    try:
        WindowsError
    except NameError:
        WindowsError = None
    
    if excluded_patterns is None:
        excluded_patterns = []
    
    names = os.listdir(src)
    
    os.makedirs(dst)
    errors = []
    for name in names:
        ignore = False
        for pattern in excluded_patterns:
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
        if not WindowsError is None and isinstance(why, WindowsError):
            pass
        else:
            errors.extend((src, dst, str(why)))
    if errors:
        raise shutil.Error, errors
