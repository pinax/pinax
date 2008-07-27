#!/usr/bin/env python
import os
import subprocess
import shutil

PROJECT='simplejson'

def _get_version():
    from pkg_resources import PathMetadata, Distribution
    egg_info = PROJECT + '.egg-info'
    base_dir = os.path.dirname(egg_info)
    metadata = PathMetadata(base_dir, egg_info)
    dist_name = os.path.splitext(os.path.basename(egg_info))[0]
    dist = Distribution(base_dir, project_name=dist_name, metadata=metadata)
    return dist.version
VERSION = _get_version()

PUDGE = '/Library/Frameworks/Python.framework/Versions/2.4/bin/pudge'
#PUDGE = 'pudge'

res = subprocess.call([
    PUDGE, '-v', '-d', 'docs', '-m', PROJECT,
    '-l', '%s %s' % (PROJECT, VERSION),
    '--theme=green'
])
if not res:
    shutil.copyfile('docs/module-simplejson.html', 'docs/index.html')
raise SystemExit(res)
