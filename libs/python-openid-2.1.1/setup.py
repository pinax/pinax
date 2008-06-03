import sys
import os

from distutils.core import setup

if 'sdist' in sys.argv:
    os.system('./admin/makedoc')

version = '[library version:2.1.1]'[17:-1]

setup(
    name='python-openid',
    version=version,
    description='OpenID support for servers and consumers.',
    long_description='''This is a set of Python packages to support use of
the OpenID decentralized identity system in your application.  Want to enable
single sign-on for your web site?  Use the openid.consumer package.  Want to
run your own OpenID server? Check out openid.server.  Includes example code
and support for a variety of storage back-ends.''',
    url='http://openidenabled.com/python-openid/',
    packages=['openid',
              'openid.consumer',
              'openid.server',
              'openid.store',
              'openid.yadis',
              'openid.extensions',
              ],
    # license specified by classifier.
    # license=getLicense(),
    author='JanRain',
    author_email='openid@janrain.com',
    download_url='http://openidenabled.com/files/python-openid/packages/python-openid-%s.tar.gz' % (version,),
    classifiers=[
    "Development Status :: 5 - Production/Stable",
    "Environment :: Web Environment",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: Apache Software License",
    "Operating System :: POSIX",
    "Programming Language :: Python",
    "Topic :: Internet :: WWW/HTTP",
    "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: System :: Systems Administration :: Authentication/Directory",
    ],
    )
