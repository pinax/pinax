import os


VERSION = (0, 9, 0, "a", 1) # following PEP 386


def get_version():
    version = "%s.%s" % (VERSION[0], VERSION[1])
    if VERSION[2]:
        version = "%s.%s" % (version, VERSION[2])
    if VERSION[3] != "f":
        version = "%s%s%s" % (version, VERSION[3], VERSION[4])
        dev = os.environ.get("PINAX_DEV_N")
        if dev:
            version = "%s.dev%s" % (version, dev)
    return version


__version__ = get_version()