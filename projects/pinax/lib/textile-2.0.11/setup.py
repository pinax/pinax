"""This is Textile. A Humane Web Text Generator.

Textile is a XHTML generator using a simple markup developed by Dean Allen. This is a Python port with support for code validation, itex to MathML translation, Python code coloring and much more.
"""

#from distutils.core import setup
from setuptools import setup, find_packages

doclines = __doc__.split("\n")

setup(name = "textile",
      version = '2.0.11',
      description = doclines[0],
      maintainer = "Roberto A. F. De Almeida",
      maintainer_email = "roberto@dealmeida.net",
      url = "http://dealmeida.net/projects/textile/",
      download_url = "http://dom.eav.free.fr/textile-2.0.10.tar.gz",
      py_modules = ['textile'],
      platforms = ["any"],
      license = 'Freely Distributable',
      long_description = "\n".join(doclines[2:]),
     )

