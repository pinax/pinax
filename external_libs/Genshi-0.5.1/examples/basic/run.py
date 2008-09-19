#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import time

from genshi.template import TemplateLoader

def test():
    base_path = os.path.dirname(os.path.abspath(__file__))
    loader = TemplateLoader([base_path], auto_reload=True)

    start = time.clock()
    tmpl = loader.load('test.html')
    print ' --> parse stage: %.4f ms' % ((time.clock() - start) * 1000)

    data = dict(hello='<world>', skin='default', hey='ZYX', bozz=None,
                items=['Number %d' % num for num in range(1, 15)],
                prefix='#')

    print tmpl.generate(**data).render(method='html')

    times = []
    for i in range(1000):
        start = time.clock()
        list(tmpl.generate(**data))
        times.append(time.clock() - start)
        sys.stdout.write('.')
        sys.stdout.flush()
    print

    print ' --> render stage: %s ms (average)' % (
          (sum(times) / len(times) * 1000))

if __name__ == '__main__':
    if '-p' in sys.argv:
        import hotshot, hotshot.stats
        prof = hotshot.Profile("template.prof")
        benchtime = prof.runcall(test)
        stats = hotshot.stats.load("template.prof")
        stats.strip_dirs()
        stats.sort_stats('time', 'calls')
        stats.print_stats()
    else:
        test()
