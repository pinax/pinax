VERSION = (0, 7, 0, "alpha", 1)

def get_version():
    if VERSION[3] != "final":
        return "%s.%s.%s%s%s" % (VERSION[0], VERSION[1], VERSION[2], VERSION[3], VERSION[4])
    else:
        return "%s.%s.%s" % (VERSION[0], VERSION[1], VERSION[2])

__version__ = get_version()