#!/usr/bin/env python
# $Id: install.py 2428 2004-07-13 15:57:13Z goodger $
# Copyright: This file has been placed in the public domain.

"""
This is a quick & dirty installation shortcut. It is equivalent to the
command::

    python setup.py install

However, the shortcut lacks error checking and command-line option
processing.  If you need any kind of customization or help, please use
one of::

    python setup.py install --help
    python setup.py --help
"""

from distutils import core
from setup import do_setup

if __name__ == '__main__' :
    print __doc__
    core._setup_stop_after = 'config'
    dist = do_setup()
    dist.commands = ['install']
    dist.run_commands()
