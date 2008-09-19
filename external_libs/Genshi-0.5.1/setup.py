#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2006-2008 Edgewall Software
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution. The terms
# are also available at http://genshi.edgewall.org/wiki/License.
#
# This software consists of voluntary contributions made by many
# individuals. For the exact contribution history, see the revision
# history and logs, available at http://genshi.edgewall.org/log/.

from distutils.cmd import Command
from distutils.command.build_ext import build_ext
from distutils.errors import CCompilerError, DistutilsPlatformError
import doctest
from glob import glob
import os
try:
    from setuptools import setup, Extension, Feature
except ImportError:
    from distutils.core import setup, Extension
    Feature = None
import sys

sys.path.append(os.path.join('doc', 'common'))
try:
    from doctools import build_doc, test_doc
except ImportError:
    build_doc = test_doc = None


class optional_build_ext(build_ext):
    # This class allows C extension building to fail.
    def run(self):
        try:
            build_ext.run(self)
        except DistutilsPlatformError:
            self._unavailable()

    def build_extension(self, ext):
        try:
            build_ext.build_extension(self, ext)
        except CCompilerError, x:
            self._unavailable()

    def _unavailable(self):
        print '*' * 70
        print """WARNING:
An optional C extension could not be compiled, speedups will not be
available."""
        print '*' * 70


if Feature:
    speedups = Feature(
        "optionial C speed-enhancements",
        standard = True,
        ext_modules = [
            Extension('genshi._speedups', ['genshi/_speedups.c']),
        ],
    )
else:
    speedups = None

setup(
    name = 'Genshi',
    version = '0.5.1',
    description = 'A toolkit for generation of output for the web',
    long_description = \
"""Genshi is a Python library that provides an integrated set of
components for parsing, generating, and processing HTML, XML or
other textual content for output generation on the web. The major
feature is a template language, which is heavily inspired by Kid.""",
    author = 'Edgewall Software',
    author_email = 'info@edgewall.org',
    license = 'BSD',
    url = 'http://genshi.edgewall.org/',
    download_url = 'http://genshi.edgewall.org/wiki/Download',
    zip_safe = True,

    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Markup :: HTML',
        'Topic :: Text Processing :: Markup :: XML'
    ],
    keywords = ['python.templating.engines'],
    packages = ['genshi', 'genshi.filters', 'genshi.template'],
    test_suite = 'genshi.tests.suite',

    extras_require = {
        'i18n': ['Babel>=0.8'],
        'plugin': ['setuptools>=0.6a2']
    },
    entry_points = """
    [babel.extractors]
    genshi = genshi.filters.i18n:extract[i18n]
    
    [python.templating.engines]
    genshi = genshi.template.plugin:MarkupTemplateEnginePlugin[plugin]
    genshi-markup = genshi.template.plugin:MarkupTemplateEnginePlugin[plugin]
    genshi-text = genshi.template.plugin:TextTemplateEnginePlugin[plugin]
    """,

    features = {'speedups': speedups},
    cmdclass = {'build_doc': build_doc, 'test_doc': test_doc,
                'build_ext': optional_build_ext}
)
