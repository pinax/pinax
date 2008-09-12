#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import time

import kid

def test():
    base_path = os.path.dirname(os.path.abspath(__file__))
    kid.path = kid.TemplatePath([base_path])

    ctxt = dict(hello='<world>', hey='ZYX', bozz=None,
                items=['Number %d' % num for num in range(1, 15)],
                prefix='#')

    start = time.clock()
    template = kid.Template(file='test.kid', **ctxt)
    print ' --> parse stage: %.4f ms' % ((time.clock() - start) * 1000)

    for output in template.generate():
        sys.stdout.write(output)
    print

    times = []
    for i in range(1000):
        start = time.clock()
        list(template.generate())
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
