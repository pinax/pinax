import os

PINAX_SVN_LOCATION = 'http://svn.pinaxproject.com/pinax/trunk'

try:
    import pip
except ImportError:
    pass
else:
    import sys
    from pkg_resources import get_distribution, parse_version
    version = get_distribution('pip').version
    if parse_version(version) < parse_version('0.3.1'):
        print 'ERROR: this script requires pip 0.3.1 or greater.'
        print 'Please upgrade your pip %s to create a Pinax virtualenv.' % version
        sys.exit(101)

def extend_parser(parser):
    parser.add_option(
        '--svn',
        metavar='DIR_OR_URL',
        dest='pinax_svn',
        default=PINAX_SVN_LOCATION,
        help='Location of a svn directory or URL to use for the installation of Pinax'
    )

def adjust_options(options, args):
    if not args:
        return # caller will raise error

def after_install(options, home_dir):
    base_dir = os.path.dirname(home_dir)
    src_dir = join(home_dir, 'src')
    pip = join(home_dir, 'bin', 'pip')
    easy_install = join(home_dir, 'bin', 'easy_install')
    pinax_svn = options.pinax_svn
    if os.path.exists(pinax_svn):
        # A directory
        pinax_dir = os.path.abspath(pinax_svn)
        logger.notify('Using existing Pinax at %s' % pinax_svn)
    else:
        pinax_dir = join(src_dir, 'pinax')
        logger.notify('Fetching Pinax from %s to %s' % (pinax_svn, pinax_dir))
        fs_ensure_dir(src_dir)
        call_subprocess(['svn', 'checkout', '--quiet', pinax_svn, pinax_dir],
                        show_stdout=True)
    logger.indent += 2
    try:
        logger.notify('Installing pip')
        call_subprocess([easy_install, '--quiet', 'pip'],
                        filter_stdout=filter_lines, show_stdout=False)
        logger.notify('Installing Django 1.0.2')
        call_subprocess([pip, 'install', 'Django', '--quiet'],
                        filter_stdout=filter_lines, show_stdout=False)
        logger.notify('Installing Pinax')
        call_subprocess([pip, 'install', '-e', pinax_dir, '--quiet'],
                        filter_stdout=filter_lines, show_stdout=False)
    finally:
        logger.indent -= 2
    logger.notify('Now activate the newly created virtualenv by running in %s: '
                  % home_dir)
    logger.indent += 2
    logger.notify("'source /bin/activate' on Linux/Unix/Mac OS "
                  "or '\\bin\\activate.bat' on Windows")
    logger.indent -= 2
    logger.notify('Pinax environment created successfully.')

def fs_ensure_dir(dir):
    if not os.path.exists(dir):
        logger.info('Creating directory %s' % dir)
        os.makedirs(dir)

def filter_lines(line):
    if not line.strip():
        return Logger.DEBUG
    for prefix in ['Searching for', 'Reading ', 'Best match: ', 'Processing ',
                   'Moving ', 'Adding ', 'running ', 'writing ', 'Creating ',
                   'creating ', 'Copying ', 'warning: manifest_maker']:
        if line.startswith(prefix):
            return Logger.DEBUG
    return Logger.NOTIFY
