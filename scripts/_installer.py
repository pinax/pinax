import os
import sys

PINAX_GIT_LOCATION = 'git://github.com/pinax/pinax.git'
PINAX_PYPI = 'http://pypi.pinaxproject.com'
PINAX_MUST_HAVES = {
    'setuptools-git': ('0.3.4', 'setuptools_git-0.3.4.tar.gz'),
    'setuptools-dummy': ('0.0.3', 'setuptools_dummy-0.0.3.tar.gz'),
    'Django': ('1.0.3', 'Django-1.0.3.tar.gz'),
    'pip': ('0.4', 'pip-0.4.tar.gz'),
}

DJANGO_VERSIONS = (
    '1.0.3',
#    '1.1',
)

JAUNTY_FIX = """/usr/lib/python2.6/dist-packages
/var/lib/python-support/python2.6
/usr/local/lib/python2.6/dist-packages
"""

if sys.platform == 'win32':
    GIT_CMD = 'git.cmd'
    PIP_CMD = 'pip.exe'
    EASY_INSTALL_CMD = 'easy_install.exe'
    extra = {'shell': True}
else:
    GIT_CMD = 'git'
    PIP_CMD = 'pip'
    EASY_INSTALL_CMD = 'easy_install'
    extra = {}

# Bailing if "~/.pydistutils.cfg" exists
pydistutils = os.path.expanduser('~/.pydistutils.cfg')
if os.path.exists(pydistutils):
    print "ERROR: Please make sure you remove any previous custom paths from"
    print "your %s file." % pydistutils
    sys.exit(3)

def winpath(path):
    if sys.platform == 'win32':
        if not os.path.exists(path):
            os.makedirs(path)
        import win32api
        # get the stupid short name on Windows to prevent dying
        # because of spaces in the command name
        return win32api.GetShortPathName(path)
    return path

def resolve_command(cmd, path=None, pathext=None):
    """
    Searches the PATH for the given executable and returns the normalized path
    """
    # save the path searched for for later fallback
    searched_for_path = path
    if path is None:
        path = os.environ.get('PATH', []).split(os.pathsep)
    if isinstance(path, basestring):
        path = [path]
    # check if there are funny path extensions for executables, e.g. Windows
    if pathext is None:
        pathext = os.environ.get('PATHEXT', '.COM;.EXE;.BAT;.CMD').split(os.pathsep)
    # don't use extensions if the command ends with one of them
    for ext in pathext:
        if cmd.endswith(ext):
            pathext = ['']
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

try:
    import pip
except ImportError:
    pass
else:
    from pkg_resources import get_distribution, parse_version
    version = get_distribution('pip').version
    if parse_version(version) == parse_version('0.3dev'):
        print 'ERROR: this script requires pip 0.3.1 or greater.'
        print 'Since you decided to use a development version of pip, please make sure you are using a recent one.'
        sys.exit(101)
    elif parse_version(version) < parse_version('0.3.1'):
        print 'ERROR: this script requires pip 0.3.1 or greater.'
        print 'Please upgrade your pip %s to create a Pinax virtualenv.' % version
        sys.exit(101)

def extend_parser(parser):
    parser.add_option("-s", "--source",
        metavar="DIR_OR_URL", dest="pinax_source", default=PINAX_GIT_LOCATION,
        help="Location of the Pinax source to use for the installation")
    parser.add_option("-r", "--release",
        metavar="RELEASE_VERSION", dest="release", default=None,
        help="Release version of Pinax to bootstrap")
    parser.add_option("-d", "--development",
        action="store_true", dest="development",
        help="Setup development environment")
    parser.add_option("--django-version",
        metavar="DJANGO_VERSION", dest="django_version", default=None,
        help="The version of Django to be installed, e.g. --django-version=1.0.3 will install Django 1.0.3. The default is 1.0.3.")

def adjust_options(options, args):
    """
    You can change options here, or change the args (if you accept
    different kinds of arguments, be sure you modify ``args`` so it is
    only ``[DEST_DIR]``).
    """
    if options.release and options.development:
        print "ERROR: please use --development without providing a --release version."
        sys.exit(101)
    if options.django_version:
        if options.django_version not in DJANGO_VERSIONS:
            print "ERROR: this Django version is not supported."
            print "Use one of those: %s" % ", ".join(DJANGO_VERSIONS)
            sys.exit(101)
        django_tarball = 'Django-%s.tar.gz' % options.django_version
        PINAX_MUST_HAVES['django'] = (options.django_version, django_tarball)
    if not args:
        return # caller will raise error

def install_base(easy_install, requirements_dir, packages):
    """
    Installs pip from the bundled tarball if existing
    """
    for pkg in packages:
        version, filename = packages[pkg]
        src = join(requirements_dir, 'base', filename)
        if not os.path.exists(src):
            # get it from the PyPI
            src = '%s==%s' % (pkg, version)
        logger.notify('Installing %s %s' % (pkg, version))
        call_subprocess([easy_install, '--quiet', '--always-copy',
                        '--always-unzip', '--find-links', PINAX_PYPI, src],
                        filter_stdout=filter_lines, show_stdout=False)

def release_files_exist(release_dir, requirements_file):
    f = open(requirements_file)
    requirements = f.read()
    f.close()
    requirements = requirements.splitlines()
    available_requirements, missing_requirements = [], []
    result = True
    for no, line in enumerate(requirements):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        requirement = os.path.normpath(join(release_dir, line))
        if not os.path.exists(requirement):
            result = False
            missing_requirements.append(requirement)
        else:
            available_requirements.append(requirement)
    if result:
        return True, available_requirements
    else:
        return False, missing_requirements

def after_install(options, home_dir):
    this_dir = os.path.dirname(__file__)
    home_dir, lib_dir, inc_dir, bin_dir = path_locations(home_dir)
    src_dir = join(home_dir, 'src')
    parent_dir = join(this_dir, '..')

    python = resolve_command(expected_exe, bin_dir)
    easy_install = resolve_command(EASY_INSTALL_CMD, bin_dir)

    # pip and setuptools-git is required in any case
    requirements_dir = join(parent_dir, 'requirements')
    install_base(easy_install, requirements_dir, PINAX_MUST_HAVES)

    # resolve path to pip
    pip = resolve_command(PIP_CMD, bin_dir)

    version_file = join(parent_dir, 'VERSION')
    if os.path.exists(version_file) and not options.release:
        f = open(version_file)
        version = f.read()
        f.close()
        version = "".join(version.splitlines())
        if version:
            options.release = version

    # FIXME we really should get that fixed in virtualenv upstream for Jaunty
    if (not options.no_site_packages and
            os.path.exists('/usr/lib/python2.6/dist-packages')):
        jaunty_path_fix = join(lib_dir, 'site-packages', 'jaunty-fix.pth')
        f = open(jaunty_path_fix, 'wb')
        f.write(JAUNTY_FIX)
        f.close()

    if options.development:
        logger.notify('Going to setup a Pinax development environment.')
        # For developers and other crazy trunk lovers
        source = options.pinax_source
        if os.path.exists(source):
            # A directory was given as a source for bootstrapping
            pinax_dir = winpath(os.path.realpath(source))
            logger.notify('Using existing Pinax at %s' % source)
        else:
            # Go and get Pinax
            pinax_dir = join(src_dir, 'pinax')
            if not os.path.exists(src_dir):
                logger.info('Creating directory %s' % src_dir)
                os.makedirs(src_dir)
            git = resolve_command(GIT_CMD)
            if os.path.exists(join(pinax_dir, '.git')):
                logger.notify('Found Pinax in %s. Updating' % pinax_dir)
                call_subprocess([git, 'pull'], show_stdout=True, cwd=pinax_dir)
            else:
                logger.notify('Fetching Pinax from %s to %s' % (source, pinax_dir))
                call_subprocess([git, 'clone', source, pinax_dir],
                                show_stdout=True)
        logger.indent += 2
        try:
            logger.notify('Installing Pinax')
            call_subprocess([python, 'setup.py', 'develop', '--quiet'],
                            filter_stdout=filter_lines, show_stdout=False,
                            cwd=pinax_dir)
        finally:
            logger.indent -= 2
        logger.notify('Please follow the documentation to continue.')
    elif options.release:
        # release should *never* touch the Internet.
        logger.notify('Going to install a full Pinax %s release.' % options.release)
        release_dir = join(requirements_dir, options.release)
        # We use easy_install for now, as long as pip can't be run on Windows
        # call_subprocess([pip, 'install', '--upgrade',
        #         '--requirement', os.path.abspath(join(release_dir, 'full.txt')),
        #         '--environment', home_dir], show_stdout=True, cwd=release_dir)
        requirements_file = os.path.realpath(join(release_dir, 'full.txt'))
        if not os.path.exists(requirements_file):
            print "ERROR: no requirements were found for version %s." % options.release
            sys.exit(101)

        # check if this is a full release with bundled packages
        result, requirements = release_files_exist(release_dir, requirements_file)
        # get the packages from the PyPI, requires internet connection
        if not result:
            print "This release does not have all the required requirements:"
            for line in requirements:
                print "    %s" % os.path.basename(line)
            sys.exit(101)
            
        for no, line in enumerate(requirements):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            logger.notify('Installing %s' % line)
            call_subprocess([easy_install, '--quiet',
                            '--always-unzip', '--find-links', PINAX_PYPI, line],
                            filter_stdout=filter_lines, show_stdout=False)

        logger.notify("Please activate the newly created virtualenv by running in '%s': "
                      % home_dir)
        logger.indent += 2
        logger.notify("'source bin/activate' on Linux/Unix/Mac OS "
                      "or '.\\Scripts\\activate.bat' on Windows")
        logger.indent -= 2
        logger.notify('Pinax environment created successfully.')
    else:
        logger.notify("Cannot locate a VERSION file for release. You are "
            "likely not running from a release tarball. Perhaps you meant to "
            "use --development")


def filter_lines(line):
    if not line.strip():
        return Logger.DEBUG
    for prefix in ['Searching for', 'Reading ', 'Best match: ', 'Processing ',
                   'Moving ', 'Adding ', 'running ', 'writing ', 'Creating ',
                   'creating ', 'Copying ', 'warning: manifest_maker',
                   'zip_safe flag not set', 'Installed', 'Finished']:
        if line.startswith(prefix):
            return Logger.DEBUG
    for suffix in ['module references __file__', 'module references __path__',
                   'inspect.getsourcefile']:
        if line.endswith(suffix):
            return Logger.DEBUG
    return Logger.NOTIFY
