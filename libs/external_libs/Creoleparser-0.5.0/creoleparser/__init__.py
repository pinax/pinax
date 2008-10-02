# __init__.py
#
# Copyright (c) 2007 Stephen Day
#
# This module is part of Creoleparser and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php
#
"""
This is a Python implementation of a parser for the Creole wiki markup language.
The specification of that can be found at http://wikicreole.org/wiki/Creole1.0

Basic Usage
===========
>>> from creoleparser import text2html

Simply call the text2html() function with one argument (the text to be parsed):

>>> print text2html("Some real **simple** mark-up"),
<p>Some real <strong>simple</strong> mark-up</p>

To customize things a little, create your own dialect and parser:

>>> from creoleparser.dialects import Creole10
>>> from creoleparser.core import Parser

>>> my_dialect=Creole10(wiki_links_base_url='http://www.mysite.net/',
... interwiki_links_base_urls=dict(wikicreole='http://wikicreole.org/wiki/'))

>>> my_parser = Parser(dialect=my_dialect)

>>> print my_parser("[[Home]] and [[wikicreole:Home]]"),
<p><a href="http://www.mysite.net/Home">Home</a> and <a href="http://wikicreole.org/wiki/Home">wikicreole:Home</a></p>

If you want pure Creole 1.0 (i.e., no additions), use creole2html() instead of text2html().

"""

from core import Parser
from dialects import Creole10

__docformat__ = 'restructuredtext en'

creole2html = Parser(dialect=Creole10(wiki_links_base_url='http://www.wikicreole.org/wiki/',
                             interwiki_links_base_urls={'Ohana':'http://wikiohana.net/cgi-bin/wiki.pl/'},
                         use_additions=False,no_wiki_monospace=True))
"""This is a pure Creole 1.0 parser created for convenience"""

creole_to_xhtml = creole2html
"""Same as creole2html"""

text2html = Parser(dialect=Creole10(wiki_links_base_url='http://www.wikicreole.org/wiki/',
                             interwiki_links_base_urls={'Ohana':'http://wikiohana.net/cgi-bin/wiki.pl/'},
                         use_additions=True,no_wiki_monospace=False))
"""This is a Creole 1.0 parser (+ additions) created for convenience"""

def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
