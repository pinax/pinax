#!/usr/bin/env python
import sys

try:
    import pinax
except ImportError:
    sys.stderr.write("Error: Can't import Pinax. Make sure you are in a "
        "virtual environment that has\nPinax installed.\n")
    sys.exit(1)
else:
    import pinax.env

from django.core.management import execute_from_command_line


pinax.env.setup_environ(__file__)


if __name__ == "__main__":
    execute_from_command_line()
