import os
import os.path
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
prev = ''
while sys.path[0] != prev:
    try:
        import DocutilsTestSupport
        break
    except ImportError:
        prev = sys.path[0]
        sys.path[0] = os.path.dirname(prev)
sys.path.pop(0)
