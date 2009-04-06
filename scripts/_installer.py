import os
import sys

PINAX_GIT_LOCATION = 'git://github.com/pinax/pinax.git'

def resolve_executable(exe):
    # searches the current $PATH for the given executable and returns the
    # full path, borrowed from virtualenv.
    if os.path.abspath(exe) != exe:
        for path in os.environ.get('PATH', '').split(os.pathsep):
            if os.path.exists(os.path.join(path, exe)):
                exe = os.path.join(path, exe)
                break
    if not os.path.exists(exe):
        print "ERROR: this script requires %s." % exe
        print "Please install it to create a Pinax virtualenv."
        sys.exit(3)
    return exe

if sys.platform == 'win32':
    GIT_CMD = 'git.cmd'
    extra = {'shell': True}
else:
    GIT_CMD = 'git'
    extra = {}
GIT_CMD = resolve_executable(GIT_CMD)

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
        '-r', '--repository',
        metavar='DIR_OR_URL',
        dest='pinax_git',
        default=PINAX_GIT_LOCATION,
        help='Location of a Git repository to use for the installation of Pinax'
    )

def adjust_options(options, args):
    if not args:
        return # caller will raise error

def after_install(options, home_dir):
    base_dir = os.path.dirname(home_dir)
    src_dir = join(home_dir, 'src')
    if sys.platform == 'win32':
        bin_dir = join(home_dir, 'Scripts')
    else:
        bin_dir = join(home_dir, 'bin')
    pinax_git = options.pinax_git
    if os.path.exists(pinax_git):
        # A directory was given as a source for bootstrapping
        pinax_dir = os.path.abspath(pinax_git)
        logger.notify('Using existing Pinax at %s' % pinax_git)
    else:
        # Go and checkout Pinax
        pinax_dir = join(src_dir, 'pinax')
        logger.notify('Fetching Pinax from %s to %s' % (pinax_git, pinax_dir))
        if not os.path.exists(src_dir):
            logger.info('Creating directory %s' % src_dir)
            os.makedirs(src_dir)
        call_subprocess(['git', 'clone', '--quiet', pinax_git, pinax_dir],
                        show_stdout=True)
    logger.indent += 2
    try:
        logger.notify('Installing pip')
        call_subprocess([join(bin_dir, 'easy_install'), '--quiet', 'pip'],
                        filter_stdout=filter_lines, show_stdout=False)
        logger.notify('Installing Django 1.0.2')
        call_subprocess(['pip', '-E', home_dir, 'install', 'Django', '--quiet'],
                        filter_stdout=filter_lines, show_stdout=False)
        logger.notify('Installing Pinax')
        call_subprocess(['pip', '-E', home_dir, 'install', '-e', pinax_dir, '--quiet'],
                        filter_stdout=filter_lines, show_stdout=False)
    finally:
        logger.indent -= 2
    logger.notify("Now activate the newly created virtualenv by running in '%s': "
                  % home_dir)
    logger.indent += 2
    logger.notify("'source bin/activate' on Linux/Unix/Mac OS "
                  "or '\\bin\\activate.bat' on Windows")
    logger.indent -= 2
    logger.notify('Pinax environment created successfully.')

def filter_lines(line):
    if not line.strip():
        return Logger.DEBUG
    for prefix in ['Searching for', 'Reading ', 'Best match: ', 'Processing ',
                   'Moving ', 'Adding ', 'running ', 'writing ', 'Creating ',
                   'creating ', 'Copying ', 'warning: manifest_maker']:
        if line.startswith(prefix):
            return Logger.DEBUG
    return Logger.NOTIFY
