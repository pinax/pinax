#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    print 'setuptools not installed, using distutils.core'
    print 'please ignore error message about "install_requires"'
    from distutils.core import setup


setup(name='Creoleparser',
      version='0.5.0',
      install_requires=['Genshi>=0.4'],
      description='Parser for the Creole common wiki markup language',
      author='Stephen Day',
      author_email='stephen.h.day@gm**l.com',
      url='http://creoleparser.googlepages.com',
      packages=['creoleparser'],
      license = 'MIT',
      zip_safe = False,
      classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Markup',
        'Topic :: Text Processing :: Markup :: HTML',
        'Topic :: Text Processing :: Markup :: XML' 
        ],
      long_description = """\
What is Creoleparser?
---------------------

Creoleparser is a Python library for converting Creole wiki markup
for output on the web. It is a full implementation of the Creole 1.0
specification and aims to follow the spec exactly.

What is Creole?
---------------

From wikicreole.org:
  Creole is a common wiki markup language to be used across different
  wikis. It's not replacing existing markup but instead enabling wiki
  users to transfer content seamlessly across wikis, and for novice
  users to contribute more easily.

Find out more about Creole at <http://www.wikicreole.org>
"""
     )

