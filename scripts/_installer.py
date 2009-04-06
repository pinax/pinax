import os
import sys

PINAX_GIT_LOCATION = 'git://github.com/pinax/pinax.git'

if sys.platform == 'win32':
    BIN_DIR = 'Scripts'
    GIT_CMD = 'git.cmd'
    PIP_CMD = 'pip.exe'
    EASY_INSTALL_CMD = 'easy_install.exe'
    extra = {'shell': True}
else:
    BIN_DIR = 'bin'
    GIT_CMD = 'git'
    PIP_CMD = 'pip'
    EASY_INSTALL_CMD = 'easy_install'
    extra = {}

def windows_path(path):
    if sys.platform == 'win32':
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
                cmd = os.path.join(path, cmd)
                break
    cmd = windows_path(cmd)
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
    if parse_version(version) < parse_version('0.3.1'):
        print 'ERROR: this script requires pip 0.3.1 or greater.'
        print 'Please upgrade your pip %s to create a Pinax virtualenv.' % version
        sys.exit(101)

def extend_parser(parser):
    parser.add_option(
        '-s', '--source',
        metavar='DIR_OR_URL',
        dest='pinax_source',
        default=PINAX_GIT_LOCATION,
        help='Location of the Pinax source to use for the installation',
    )

def adjust_options(options, args):
    if not args:
        return # caller will raise error

def after_install(options, home_dir):
    home_dir = windows_path(home_dir)
    base_dir = os.path.dirname(home_dir)
    src_dir = join(home_dir, 'src')
    bin_dir = join(home_dir, BIN_DIR)
    pinax_source = options.pinax_source
    if os.path.exists(pinax_source):
        # A directory was given as a source for bootstrapping
        pinax_dir = os.path.abspath(pinax_source)
        logger.notify('Using existing Pinax at %s' % pinax_source)
    else:
        # Go and checkout Pinax
        pinax_dir = join(src_dir, 'pinax')
        logger.notify('Fetching Pinax from %s to %s' % (pinax_source, pinax_dir))
        if not os.path.exists(src_dir):
            logger.info('Creating directory %s' % src_dir)
            os.makedirs(src_dir)
        git = resolve_command(GIT_CMD)
        call_subprocess([git, 'clone', '--quiet', pinax_source, pinax_dir],
                        show_stdout=True)
    logger.indent += 2
    try:
        logger.notify('Installing pip')
        easy_install = resolve_command(EASY_INSTALL_CMD, bin_dir)
        call_subprocess([easy_install, '--quiet', '--always-copy', 'pip'],
                        filter_stdout=filter_lines, show_stdout=False)
        pip = resolve_command(PIP_CMD, bin_dir)
        logger.notify('Installing Django')
        call_subprocess([pip, '--environment', home_dir, 'install', 'Django', '--quiet'],
                        filter_stdout=filter_lines, show_stdout=False)
        logger.notify('Installing Pinax')
        call_subprocess([pip, '--environment', home_dir, 'install', '--editable', pinax_dir, '--quiet'],
                        filter_stdout=filter_lines, show_stdout=False)
    finally:
        logger.indent -= 2
    logger.notify("Now activate the newly created virtualenv by running in '%s': "
                  % home_dir)
    logger.indent += 2
    logger.notify("'source bin/activate' on Linux/Unix/Mac OS "
                  "or '.\\Scripts\\activate.bat' on Windows")
    logger.indent -= 2
    logger.notify('Pinax environment created successfully.')

def filter_lines(line):
    if not line.strip():
        return Logger.DEBUG
    for prefix in ['Searching for', 'Reading ', 'Best match: ', 'Processing ',
                   'Moving ', 'Adding ', 'running ', 'writing ', 'Creating ',
                   'creating ', 'Copying ', 'warning: manifest_maker',
                   'zip_safe flag not set']:
        if line.startswith(prefix):
            return Logger.DEBUG
    for suffix in ['module references __file__']:
        if line.endswith(suffix):
            return Logger.DEBUG
    return Logger.NOTIFY
