VERSION = (0, 7, 0, "rc", 1)

def get_version():
    version = '%s.%s' % (VERSION[0], VERSION[1])
    if VERSION[2]:
        version = '%s.%s' % (version, VERSION[2])
    if VERSION[3]:
        version = '%s%s' % (version, VERSION[3])
        if VERSION[3] != 'final':
            version = '%s%s' % (version, VERSION[4])
    return version

__version__ = get_version()