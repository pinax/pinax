# -*- encoding: utf-8 -*-
# Template language benchmarks
#
# Objective: Test general templating features using a small template

from cgi import escape
import os
from StringIO import StringIO
import sys
import timeit

__all__ = ['clearsilver', 'mako', 'django', 'kid', 'genshi', 'genshi_text',
           'simpletal']

def genshi(dirname, verbose=False):
    from genshi.template import TemplateLoader
    loader = TemplateLoader([dirname], auto_reload=False)
    template = loader.load('template.html')
    def render():
        data = dict(title='Just a test', user='joe',
                    items=['Number %d' % num for num in range(1, 15)])
        return template.generate(**data).render('xhtml')

    if verbose:
        print render()
    return render

def genshi_text(dirname, verbose=False):
    from genshi.core import escape
    from genshi.template import TemplateLoader, NewTextTemplate
    loader = TemplateLoader([dirname], auto_reload=False)
    template = loader.load('template.txt', cls=NewTextTemplate)
    def render():
        data = dict(escape=escape, title='Just a test', user='joe',
                    items=['Number %d' % num for num in range(1, 15)])
        return template.generate(**data).render('text')

    if verbose:
        print render()
    return render

def mako(dirname, verbose=False):
    from mako.lookup import TemplateLookup
    lookup = TemplateLookup(directories=[dirname], filesystem_checks=False)
    template = lookup.get_template('template.html')
    def render():
        data = dict(title='Just a test', user='joe',
                    list_items=['Number %d' % num for num in range(1, 15)])
        return template.render(**data)
    if verbose:
        print render()
    return render

def cheetah(dirname, verbose=False):
    # FIXME: infinite recursion somewhere... WTF?
    try:
        from Cheetah.Template import Template
    except ImportError:
        print>>sys.stderr, 'Cheetah not installed, skipping'
        return lambda: None
    class MyTemplate(Template):
        def serverSidePath(self, path): return os.path.join(dirname, path)
    filename = os.path.join(dirname, 'template.tmpl')
    template = MyTemplate(file=filename)

    def render():
        template = MyTemplate(file=filename,
                              searchList=[{'title': 'Just a test', 'user': 'joe',
                                           'items': [u'Number %d' % num for num in range(1, 15)]}])
        return template.respond()

    if verbose:
        print render()
    return render

def clearsilver(dirname, verbose=False):
    try:
        import neo_cgi
    except ImportError:
        print>>sys.stderr, 'ClearSilver not installed, skipping'
        return lambda: None
    neo_cgi.update()
    import neo_util
    import neo_cs
    def render():
        hdf = neo_util.HDF()
        hdf.setValue('hdf.loadpaths.0', dirname)
        hdf.setValue('title', escape('Just a test'))
        hdf.setValue('user', escape('joe'))
        for num in range(1, 15):
            hdf.setValue('items.%d' % (num - 1), escape('Number %d' % num))
        cs = neo_cs.CS(hdf)
        cs.parseFile('template.cs')
        return cs.render()

    if verbose:
        print render()
    return render

def django(dirname, verbose=False):
    try:
        from django.conf import settings
        settings.configure(TEMPLATE_DIRS=[os.path.join(dirname, 'templates')])
    except ImportError:
        print>>sys.stderr, 'Django not installed, skipping'
        return lambda: None
    from django import template, templatetags
    from django.template import loader
    templatetags.__path__.append(os.path.join(dirname, 'templatetags'))
    tmpl = loader.get_template('template.html')

    def render():
        data = {'title': 'Just a test', 'user': 'joe',
                'items': ['Number %d' % num for num in range(1, 15)]}
        return tmpl.render(template.Context(data))

    if verbose:
        print render()
    return render

def kid(dirname, verbose=False):
    try:
        import kid
    except ImportError:
        print>>sys.stderr, "Kid not installed, skipping"
        return lambda: None
    kid.path = kid.TemplatePath([dirname])
    template = kid.load_template('template.kid').Template
    def render():
        return template(
            title='Just a test', user='joe',
            items=['Number %d' % num for num in range(1, 15)]
        ).serialize(output='xhtml')

    if verbose:
        print render()
    return render

def simpletal(dirname, verbose=False):
    try:
        from simpletal import simpleTAL, simpleTALES
    except ImportError:
        print>>sys.stderr, "SimpleTAL not installed, skipping"
        return lambda: None
    fileobj = open(os.path.join(dirname, 'base.html'))
    base = simpleTAL.compileHTMLTemplate(fileobj)
    fileobj.close()
    fileobj = open(os.path.join(dirname, 'template.html'))
    template = simpleTAL.compileHTMLTemplate(fileobj)
    fileobj.close()
    def render():
        ctxt = simpleTALES.Context(allowPythonPath=1)
        ctxt.addGlobal('base', base)
        ctxt.addGlobal('title', 'Just a test')
        ctxt.addGlobal('user', 'joe')
        ctxt.addGlobal('items', ['Number %d' % num for num in range(1, 15)])
        buf = StringIO()
        template.expand(ctxt, buf)
        return buf.getvalue()

    if verbose:
        print render()
    return render

def run(engines, number=2000, verbose=False):
    basepath = os.path.abspath(os.path.dirname(__file__))
    for engine in engines:
        dirname = os.path.join(basepath, engine)
        if verbose:
            print '%s:' % engine.capitalize()
            print '--------------------------------------------------------'
        else:
            print '%s:' % engine.capitalize(),
        t = timeit.Timer(setup='from __main__ import %s; render = %s(r"%s", %s)'
                               % (engine, engine, dirname, verbose),
                         stmt='render()')
        time = t.timeit(number=number) / number
        if verbose:
            print '--------------------------------------------------------'
        print '%.2f ms' % (1000 * time)
        if verbose:
            print '--------------------------------------------------------'


if __name__ == '__main__':
    engines = [arg for arg in sys.argv[1:] if arg[0] != '-']
    if not engines:
        engines = __all__

    verbose = '-v' in sys.argv

    if '-p' in sys.argv:
        import hotshot, hotshot.stats
        prof = hotshot.Profile("template.prof")
        benchtime = prof.runcall(run, engines, number=100, verbose=verbose)
        stats = hotshot.stats.load("template.prof")
        stats.strip_dirs()
        stats.sort_stats('time', 'calls')
        stats.print_stats(.05)
    else:
        run(engines, verbose=verbose)
