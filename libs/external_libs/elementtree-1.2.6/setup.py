#!/usr/bin/env python
#
# Setup script for the elementtree library
# $Id: setup.py 2326 2005-03-17 07:45:21Z fredrik $
#
# Usage: python setup.py install
#

from distutils.core import setup

try:
    # add download_url syntax to distutils
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None
except:
    pass

DESCRIPTION="ElementTree - a light-weight XML object model for Python."

LONG_DESCRIPTION="""\
The Element type is a flexible container object, designed to store
hierarchical data structures in memory.  Element structures can be
converted to and from XML."""

setup(
    name="elementtree",
    version="1.2.6-20050316",
    author="Fredrik Lundh",
    author_email="fredrik@pythonware.com",
    url="http://effbot.org/zone/element-index.htm",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    download_url="http://effbot.org/downloads#elementtree",
    license="Python (MIT style)",
    packages=["elementtree"],
    platforms="Python 1.5.2 and later.",
    classifiers=[
        "Development Status :: 6 - Mature",
        "Operating System :: OS Independent",
        "Topic :: Text Processing :: Markup :: HTML",
        "Topic :: Text Processing :: Markup :: XML",
        ]
    )
