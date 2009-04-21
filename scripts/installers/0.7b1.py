import os
import sys

if sys.platform == 'win32':
    BIN_DIR = 'Scripts'
    GIT_CMD = 'git.cmd'
    PYTHON_CMD = 'python.exe'
    PIP_CMD = 'pip.exe'
    EASY_INSTALL_CMD = 'easy_install.exe'
    extra = {'shell': True}
else:
    BIN_DIR = 'bin'
    GIT_CMD = 'git'
    PYTHON_CMD = 'python'
    PIP_CMD = 'pip'
    EASY_INSTALL_CMD = 'easy_install'
    extra = {}

# in case the VERSION file already moved on
VERSION = "0.7b1"

def winpath(path):
    if sys.platform == 'win32':
        if not os.path.exists(path):
            os.makedirs(path)
        import win32api
        # get the stupid short name on Windows to prevent dying
        # because of spaces in the command name
        return win32api.GetShortPathName(path)
    return path

def resolve_command(cmd, default_paths=[]):
    # searches the current $PATH for the given executable and returns the
    # full path, borrowed from virtualenv.
    if os.path.abspath(cmd) != cmd:
        paths = os.environ.get('PATH', '').split(os.pathsep)
        if default_paths:
            paths.insert(0, default_paths)
        for path in paths:
            if os.path.exists(os.path.join(path, cmd)):
                path = winpath(path)
                cmd = os.path.join(path, cmd)
                break
    if not os.path.exists(cmd):
        print "ERROR: this script requires %s." % cmd
        print "Please install it to create a Pinax virtualenv."
        sys.exit(3)
    return cmd

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

def install_base(packages, easy_install, requirements_dir):
    """
    Installs pip from the bundled tarball if existing
    """
    for pkg in packages:
        distname, filename = pkg
        src = join(requirements_dir, 'base', filename)
        if not os.path.exists(src):
            # get it from the pypi
            src = distname
        call_subprocess([easy_install, '--quiet', '--always-copy', src],
                        filter_stdout=filter_lines, show_stdout=False)
        logger.notify('Installing %s.............done.' % distname)

def after_install(options, home_dir):
    this_dir = os.path.dirname(__file__)
    home_dir = winpath(os.path.abspath(home_dir))
    base_dir = os.path.dirname(home_dir)
    src_dir = join(home_dir, 'src')
    bin_dir = join(home_dir, BIN_DIR)
    parent_dir = join(parent_dir, '..')
    requirements_dir = join(parent_dir, 'requirements')

    python = resolve_command(PYTHON_CMD, bin_dir)
    easy_install = resolve_command(EASY_INSTALL_CMD, bin_dir)

    # pip and setuptools-git is required in any case
    install_base([('setuptools-git', 'setuptools_git-0.3.3.tar.gz'),
                  ('pip', 'pip-0.3.1.tar.gz')],
                  easy_install, requirements_dir)

    # resolve path to pip
    pip = resolve_command(PIP_CMD, bin_dir)

    # Use the bundled requirements file and packages if possible
    # get file: reqirements/0.7.0beta1/full.txt
    release_dir = join(requirements_dir, VERSION)
    # call_subprocess([pip, 'install', '--upgrade',
    #         '--requirement', os.path.abspath(join(release_dir, 'full.txt')),
    #         '--environment', home_dir], show_stdout=True, cwd=release_dir)
    # Use easy_install for now, as long as pip can't be run on Windows
    full_requirements_file = os.path.abspath(join(requirements_dir, 'full.txt'))
    if not os.path.exists(full_requirements_file):
        print "ERROR: no bundled requirements were found for version %s." % VERSION
        sys.exit(101)

    f = open(full_requirements_file)
    full_requirements = f.read()
    f.close()
    for line_number, line in enumerate(full_requirements.splitlines()):
        line_number += 1
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        full_requirement = join(release_dir, line)
        if os.path.exists(full_requirement):
            call_subprocess([easy_install, '--quiet', '--always-copy',
                            '--always-unzip', full_requirement],
                            filter_stdout=filter_lines,
                            show_stdout=False)
            logger.notify('Unpacking/installing %s.............done.' % line)
    logger.notify("Please activate the newly created virtualenv by running in '%s': "
                  % home_dir)
    logger.indent += 2
    logger.notify("'source bin/activate' on Linux/Unix/Mac OS "
                  "or '.\\Scripts\\activate.bat' on Windows")
    logger.indent -= 2
    logger.notify('Pinax environment created successfully.')
    logger.notify('Please follow the documentation to install all the requirements (e.g. Django).')


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
