#!/usr/bin/env python

from distutils.core import setup
import os, sys

if 'sdist' in sys.argv:
    os.system('./admin/epyrun')

# patch distutils if it can't cope with the "classifiers" or
# "download_url" keywords
if sys.version < '2.2.3':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None

version = '[library version:1.1.0]'[17:-1]

kwargs = {
    'name': "python-yadis",
    'version': version,
    'url': "http://www.openidenabled.com/yadis/libraries/python/",
    'download_url': "http://www.openidenabled.com/resources/downloads/python-yadis/python-yadis-%s.tar.gz" % (version,),
    'author': "JanRain, Inc.",
    'author_email': "openid@janrain.com",
    'description': "Yadis service discovery library.",
    'long_description': "Yadis is a protocol for discovering services "
    "applicable to a URL.  This package provides a client implementation "
    "of the Yadis protocol.",
    'packages': ['yadis',
                 ],
    'license': "LGPL",
    'classifiers': [
    "Development Status :: 5 - Production/Stable",
    "Environment :: Web Environment",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
    "Operating System :: POSIX",
    "Programming Language :: Python",
    "Topic :: Internet :: WWW/HTTP",
    "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: System :: Systems Administration :: Authentication/Directory",
    ]
    }

setup(**kwargs)
