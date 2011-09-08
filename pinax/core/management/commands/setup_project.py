import glob
import optparse
import os
import random
import re
import shutil
import sys

import pip

try:
    from pip.exceptions import InstallationError
except ImportError:
    print ("You are using an older version of pip. Please upgrade pip to "
           "0.7+ (which ships with virtualenv 1.4.7+)")
    sys.exit(1)

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
        ),
        optparse.make_option("--no-reqs",
            dest = "no_reqs",
            action = "store_true",
            help = "do not install requirements automatically"
        ),
        optparse.make_option("--allow-no-virtualenv",
            dest = "allow_no_virtualenv",
            action = "store_true",
            default = False,
            help = "turn off the requirement pip must run inside a virtual environment"
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
        
        self.setup_project(args[0], options["base"], options)
    
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
    
    def setup_project(self, destination, base, options):
        
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
                "try another name." % user_project_name
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
        
        installer = ProjectInstaller(source, destination, project_name, user_project_name)
        installer.copy()
        installer.fix_settings()
        installer.fix_deploy(project_name, user_project_name)
        print "Created project %s" % user_project_name
        if not options["no_reqs"]:
            print "Installing project requirements..."
            try:
                installer.install_reqs(not options["allow_no_virtualenv"])
            except InstallationError:
                print ("Installation of requirements failed. The project %s "
                    "has been created though.") % user_project_name
        else:
            print
            print ("Skipping requirement installation. Run pip install --no-deps "
                "-r requirements/project.txt inside the project directory.")


class ProjectInstaller(object):
    """
    Provides the methods to install a project at a given destination
    """
    
    def __init__(self, source_dir, project_dir, project_name, user_project_name):
        self.source_dir = source_dir
        self.project_dir = project_dir
        self.project_name = project_name
        self.user_project_name = user_project_name
    
    def generate_secret_key(self):
        chars = "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)"
        return "".join([random.choice(chars) for i in xrange(50)])
    
    def copy(self):
        copytree(self.source_dir, self.project_dir,
            excluded_patterns=[
                ".svn", ".pyc", "dev.db"
            ]
        )
    
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
    
    def fix_deploy(self, base, project_name):
        for deploy_file in glob.glob(os.path.join(self.project_dir, "deploy/") + "*"):
            df = open(deploy_file, "rb")
            deploy_settings = df.read()
            df.close()
            deploy_settings = deploy_settings.replace(base, project_name)
            df = open(deploy_file, "wb")
            df.write(deploy_settings)
            df.close()
    
    def install_reqs(self, require_virtualenv=True):
        # @@@ move to using Python pip APIs and not relying on the OS
        
        if sys.platform == "win32":
            PIP_CMD = "pip.exe"
        else:
            PIP_CMD = "pip"
        
        pip_cmd = resolve_command(PIP_CMD)
        requirements_file = os.path.join(self.project_dir, "requirements", "project.txt")
        
        environ = {}
        if require_virtualenv:
            environ["PIP_REQUIRE_VIRTUALENV"] = "true"
        
        pip.call_subprocess([
            pip_cmd,
            "install",
            "--requirement", requirements_file,
        ], show_stdout=True, extra_environ=environ)


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


# needed for ProjectInstaller.install_reqs
def resolve_command(cmd, path=None, pathext=None):
    """
    Searches the PATH for the given executable and returns the normalized path
    """
    # save the path searched for for later fallback
    searched_for_path = path
    if path is None:
        path = os.environ.get("PATH", []).split(os.pathsep)
    if isinstance(path, basestring):
        path = [path]
    # check if there are funny path extensions for executables, e.g. Windows
    if pathext is None:
        pathext = os.environ.get("PATHEXT", ".COM;.EXE;.BAT;.CMD").split(os.pathsep)
    # don"t use extensions if the command ends with one of them
    for ext in pathext:
        if cmd.endswith(ext):
            pathext = [""]
            break
    # check if we find the command on PATH
    for _dir in path:
        f = os.path.join(_dir, cmd)
        for ext in pathext:
            # try without extension first
            if os.path.isfile(f):
                return os.path.realpath(f)
            # then including the extension
            fext = f + ext
            if os.path.isfile(fext):
                return os.path.realpath(fext)
    # last resort: just try the searched for path
    if searched_for_path:
        cmd = os.path.join(os.path.realpath(searched_for_path), cmd)
    if not os.path.exists(cmd):
        print "ERROR: this script requires %s." % cmd
        print "Please verify it exists because it couldn't be found."
        sys.exit(3)
    return os.path.realpath(cmd)
