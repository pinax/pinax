#!/usr/bin/env python
# $Id: setup.py 4260 2006-01-09 18:28:09Z fwiemann $
# Copyright: This file has been placed in the public domain.

import sys
import os
import glob
from distutils.core import setup
from distutils.command.build_py import build_py

# From <http://groups.google.de/groups?as_umsgid=f70e3538.0404141327.6cea58ca@posting.google.com>.
from distutils.command.install import INSTALL_SCHEMES
for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']


def do_setup():
    kwargs = package_data.copy()
    extras = get_extras()
    if extras:
        kwargs['py_modules'] = extras
    if sys.hexversion >= 0x02030000:    # Python 2.3
        kwargs['classifiers'] = classifiers
    else:
        kwargs['cmdclass'] = {'build_py': dual_build_py}
    dist = setup(**kwargs)
    return dist

s5_theme_files = []
for dir in glob.glob('docutils/writers/s5_html/themes/*'):
    if os.path.isdir(dir):
        theme_files = glob.glob('%s/*' % dir)
        s5_theme_files.append((dir, theme_files))

package_data = {
    'name': 'docutils',
    'description': 'Docutils -- Python Documentation Utilities',
    'long_description': """\
Docutils is a modular system for processing documentation
into useful formats, such as HTML, XML, and LaTeX.  For
input Docutils supports reStructuredText, an easy-to-read,
what-you-see-is-what-you-get plaintext markup syntax.""", # wrap at col 60
    'url': 'http://docutils.sourceforge.net/',
    'version': '0.4',
    'author': 'David Goodger',
    'author_email': 'goodger@users.sourceforge.net',
    'license': 'public domain, Python, BSD, GPL (see COPYING.txt)',
    'platforms': 'OS-independent',
    'package_dir': {'docutils': 'docutils', '': 'extras'},
    'packages': ['docutils',
                 'docutils.languages',
                 'docutils.parsers',
                 'docutils.parsers.rst',
                 'docutils.parsers.rst.directives',
                 'docutils.parsers.rst.languages',
                 'docutils.readers',
                 'docutils.readers.python',
                 'docutils.transforms',
                 'docutils.writers',
                 'docutils.writers.html4css1',
                 'docutils.writers.pep_html',
                 'docutils.writers.s5_html',
                 'docutils.writers.latex2e',
                 'docutils.writers.newlatex2e'],
    'data_files': ([('docutils/parsers/rst/include',
                     glob.glob('docutils/parsers/rst/include/*.txt')),
                    ('docutils/writers/html4css1',
                     ['docutils/writers/html4css1/html4css1.css']),
                    ('docutils/writers/latex2e',
                     ['docutils/writers/latex2e/latex2e.tex']),
                    ('docutils/writers/newlatex2e',
                     ['docutils/writers/newlatex2e/base.tex']),
                    ('docutils/writers/pep_html',
                     ['docutils/writers/pep_html/pep.css',
                      'docutils/writers/pep_html/template.txt']),
                    ('docutils/writers/s5_html/themes',
                     ['docutils/writers/s5_html/themes/README.txt']),]
                   + s5_theme_files),
    'scripts' : ['tools/rst2html.py',
                 'tools/rst2s5.py',
                 'tools/rst2latex.py',
                 'tools/rst2newlatex.py',
                 'tools/rst2xml.py',
                 'tools/rst2pseudoxml.py'],}
"""Distutils setup parameters."""

classifiers = [
    'Development Status :: 3 - Alpha',
    'Environment :: Console',
    'Intended Audience :: End Users/Desktop',
    'Intended Audience :: Other Audience',
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'License :: Public Domain',
    'License :: OSI Approved :: Python Software Foundation License',
    'License :: OSI Approved :: BSD License',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Documentation',
    'Topic :: Software Development :: Documentation',
    'Topic :: Text Processing',
    'Natural Language :: English',      # main/default language, keep first
    'Natural Language :: Afrikaans',
    'Natural Language :: Esperanto',
    'Natural Language :: French',
    'Natural Language :: German',
    'Natural Language :: Italian',
    'Natural Language :: Russian',
    'Natural Language :: Slovak',
    'Natural Language :: Spanish',
    'Natural Language :: Swedish',]
"""Trove classifiers for the Distutils "register" command;
Python 2.3 and up."""

extra_modules = [('optparse', '1.4.1', None),
                 ('textwrap', None, None),
                 ('roman', '1.4', ['toRoman', 'fromRoman',
                                   'InvalidRomanNumeralError'])]
"""Third-party modules to install if they're not already present.
List of (module name, minimum __version__ string, [attribute names])."""

def get_extras():
    extras = []
    for module_name, version, attributes in extra_modules:
        try:
            module = __import__(module_name)
            if version and module.__version__ < version:
                raise ValueError
            for attribute in attributes or []:
                getattr(module, attribute)
            print ('"%s" module already present; ignoring extras/%s.py.'
                   % (module_name, module_name))
        except (ImportError, AttributeError, ValueError):
            extras.append(module_name)
    return extras


class dual_build_py(build_py):

    """
    This class allows the distribution of both packages *and* modules with one
    call to `distutils.core.setup()` (necessary for pre-2.3 Python).  Thanks
    to Thomas Heller.
    """

    def run(self):
        if not self.py_modules and not self.packages:
            return
        if self.py_modules:
            self.build_modules()
        if self.packages:
            self.build_packages()
        self.byte_compile(self.get_outputs(include_bytecode=0))


if __name__ == '__main__' :
    do_setup()
