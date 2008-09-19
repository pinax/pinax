#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages

import pygments

author, email = pygments.__author__[:-1].split(' <')

setup(
    name = 'Pygments',
    version = pygments.__version__,
    url = pygments.__url__,
    license = pygments.__license__,
    author = author,
    author_email = email,
    description = 'Pygments is a syntax highlighting package written in Python.',
    long_description = pygments.__doc__,
    keywords = 'syntax highlighting',
    packages = find_packages(),
    entry_points = {
        'console_scripts': [
            'pygmentize = pygments.cmdline:main',
        ],
    },
    platforms = 'any',
    zip_safe = False,
    include_package_data = True,
    classifiers = [
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: System Administrators',
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
    ]
)
