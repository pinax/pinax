VERSION = (0, 7, 3, "final")

def get_version():
    version = '%s.%s' % (VERSION[0], VERSION[1])
    if VERSION[2]:
        version = '%s.%s' % (version, VERSION[2])
    if VERSION[3] != "final":
        version = '%s%s%s' % (version, VERSION[3], VERSION[4])
    return version

__version__ = get_version()