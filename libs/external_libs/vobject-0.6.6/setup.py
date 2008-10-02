"""VObject: module for reading vCard and vCalendar files

Description
-----------

Parses iCalendar and vCard files into Python data structures, decoding the relevant encodings. Also serializes vobject data structures to iCalendar, vCard, or (expirementally) hCalendar unicode strings.

Requirements
------------

Requires python 2.4 or later, dateutil (http://labix.org/python-dateutil) 1.1 or later.

Recent changes
--------------

   * Allow unicode names for TZIDs
   * Worked around Lotus Notes use of underscores in names by just silently replacing
     with dashes
   * When allowing quoted-printable data, honor CHARSET for each line, defaulting to 
     iso-8859-1
   * Simplified directory layout, unit tests are now available via setup.py test
   * Added VAVAILABILITY support
   * Improved wrapping of unicode lines, serialize encodes unicode as utf-8 by default

For older changes, see 
   * http://vobject.skyhouseconsulting.com/history.html or 
   * http://websvn.osafoundation.org/listing.php?repname=vobject&path=/trunk/

"""

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

doclines = __doc__.splitlines()

setup(name = "vobject",
      version = "0.6.6",
      author = "Jeffrey Harris",
      author_email = "jeffrey@osafoundation.org",
      license = "Apache",
      zip_safe = True,
      url = "http://vobject.skyhouseconsulting.com",
      entry_points = { 'console_scripts': ['ics_diff = vobject.ics_diff:main'] },
      include_package_data = True,
      test_suite = "test_vobject",

      install_requires = ['python-dateutil >= 1.1'], 
      
      platforms = ["any"],
      packages = find_packages(),
      description = doclines[0],
      long_description = "\n".join(doclines[2:]),
      classifiers =  """
      Development Status :: 4 - Beta
      Environment :: Console
      License :: OSI Approved :: BSD License
      Intended Audience :: Developers
      Natural Language :: English
      Programming Language :: Python
      Operating System :: OS Independent
      Topic :: Text Processing""".strip().splitlines()
      )
