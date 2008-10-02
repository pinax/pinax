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

import doctest
import os
import shutil
import tempfile
import unittest

from genshi.template.base import TemplateSyntaxError
from genshi.template.loader import TemplateLoader
from genshi.template.text import OldTextTemplate, NewTextTemplate


class OldTextTemplateTestCase(unittest.TestCase):
    """Tests for text template processing."""

    def setUp(self):
        self.dirname = tempfile.mkdtemp(suffix='markup_test')

    def tearDown(self):
        shutil.rmtree(self.dirname)

    def test_escaping(self):
        tmpl = OldTextTemplate('\\#escaped')
        self.assertEqual('#escaped', str(tmpl.generate()))

    def test_comment(self):
        tmpl = OldTextTemplate('## a comment')
        self.assertEqual('', str(tmpl.generate()))

    def test_comment_escaping(self):
        tmpl = OldTextTemplate('\\## escaped comment')
        self.assertEqual('## escaped comment', str(tmpl.generate()))

    def test_end_with_args(self):
        tmpl = OldTextTemplate("""
        #if foo
          bar
        #end 'if foo'""")
        self.assertEqual('\n', str(tmpl.generate(foo=False)))

    def test_latin1_encoded(self):
        text = u'$foo\xf6$bar'.encode('iso-8859-1')
        tmpl = OldTextTemplate(text, encoding='iso-8859-1')
        self.assertEqual(u'x\xf6y', unicode(tmpl.generate(foo='x', bar='y')))

    def test_unicode_input(self):
        text = u'$foo\xf6$bar'
        tmpl = OldTextTemplate(text)
        self.assertEqual(u'x\xf6y', unicode(tmpl.generate(foo='x', bar='y')))

    def test_empty_lines1(self):
        tmpl = OldTextTemplate("""Your items:

        #for item in items
          * ${item}
        #end""")
        self.assertEqual("""Your items:

          * 0
          * 1
          * 2
""", tmpl.generate(items=range(3)).render())

    def test_empty_lines2(self):
        tmpl = OldTextTemplate("""Your items:

        #for item in items
          * ${item}

        #end""")
        self.assertEqual("""Your items:

          * 0

          * 1

          * 2

""", tmpl.generate(items=range(3)).render())

    def test_include(self):
        file1 = open(os.path.join(self.dirname, 'tmpl1.txt'), 'w')
        try:
            file1.write("Included\n")
        finally:
            file1.close()

        file2 = open(os.path.join(self.dirname, 'tmpl2.txt'), 'w')
        try:
            file2.write("""----- Included data below this line -----
            #include tmpl1.txt
            ----- Included data above this line -----""")
        finally:
            file2.close()

        loader = TemplateLoader([self.dirname])
        tmpl = loader.load('tmpl2.txt', cls=OldTextTemplate)
        self.assertEqual("""----- Included data below this line -----
Included
            ----- Included data above this line -----""",
                         tmpl.generate().render())


class NewTextTemplateTestCase(unittest.TestCase):
    """Tests for text template processing."""

    def setUp(self):
        self.dirname = tempfile.mkdtemp(suffix='markup_test')

    def tearDown(self):
        shutil.rmtree(self.dirname)

    def test_escaping(self):
        tmpl = NewTextTemplate('\\{% escaped %}')
        self.assertEqual('{% escaped %}', str(tmpl.generate()))

    def test_comment(self):
        tmpl = NewTextTemplate('{# a comment #}')
        self.assertEqual('', str(tmpl.generate()))

    def test_comment_escaping(self):
        tmpl = NewTextTemplate('\\{# escaped comment #}')
        self.assertEqual('{# escaped comment #}', str(tmpl.generate()))

    def test_end_with_args(self):
        tmpl = NewTextTemplate("""
{% if foo %}
  bar
{% end 'if foo' %}""")
        self.assertEqual('\n', str(tmpl.generate(foo=False)))

    def test_latin1_encoded(self):
        text = u'$foo\xf6$bar'.encode('iso-8859-1')
        tmpl = NewTextTemplate(text, encoding='iso-8859-1')
        self.assertEqual(u'x\xf6y', unicode(tmpl.generate(foo='x', bar='y')))

    def test_unicode_input(self):
        text = u'$foo\xf6$bar'
        tmpl = NewTextTemplate(text)
        self.assertEqual(u'x\xf6y', unicode(tmpl.generate(foo='x', bar='y')))

    def test_empty_lines1(self):
        tmpl = NewTextTemplate("""Your items:

{% for item in items %}\
  * ${item}
{% end %}""")
        self.assertEqual("""Your items:

  * 0
  * 1
  * 2
""", tmpl.generate(items=range(3)).render())

    def test_empty_lines2(self):
        tmpl = NewTextTemplate("""Your items:

{% for item in items %}\
  * ${item}

{% end %}""")
        self.assertEqual("""Your items:

  * 0

  * 1

  * 2

""", tmpl.generate(items=range(3)).render())

    def test_exec_with_trailing_space(self):
        """
        Verify that a code block with trailing space does not cause a syntax
        error (see ticket #127).
        """
        NewTextTemplate(u"""
          {% python
            bar = 42
          $}
        """)

    def test_exec_import(self):
        tmpl = NewTextTemplate(u"""{% python from datetime import timedelta %}
        ${timedelta(days=2)}
        """)
        self.assertEqual("""
        2 days, 0:00:00
        """, str(tmpl.generate()))

    def test_exec_def(self):
        tmpl = NewTextTemplate(u"""{% python
        def foo():
            return 42
        %}
        ${foo()}
        """)
        self.assertEqual(u"""
        42
        """, str(tmpl.generate()))

    def test_include(self):
        file1 = open(os.path.join(self.dirname, 'tmpl1.txt'), 'w')
        try:
            file1.write("Included")
        finally:
            file1.close()

        file2 = open(os.path.join(self.dirname, 'tmpl2.txt'), 'w')
        try:
            file2.write("""----- Included data below this line -----
{% include tmpl1.txt %}
----- Included data above this line -----""")
        finally:
            file2.close()

        loader = TemplateLoader([self.dirname])
        tmpl = loader.load('tmpl2.txt', cls=NewTextTemplate)
        self.assertEqual("""----- Included data below this line -----
Included
----- Included data above this line -----""", tmpl.generate().render())

    def test_include_expr(self):
         file1 = open(os.path.join(self.dirname, 'tmpl1.txt'), 'w')
         try:
             file1.write("Included")
         finally:
             file1.close()
 
         file2 = open(os.path.join(self.dirname, 'tmpl2.txt'), 'w')
         try:
             file2.write("""----- Included data below this line -----
    {% include ${'%s.txt' % ('tmpl1',)} %}
    ----- Included data above this line -----""")
         finally:
             file2.close()

         loader = TemplateLoader([self.dirname])
         tmpl = loader.load('tmpl2.txt', cls=NewTextTemplate)
         self.assertEqual("""----- Included data below this line -----
    Included
    ----- Included data above this line -----""", tmpl.generate().render())


def suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite(NewTextTemplate.__module__))
    suite.addTest(unittest.makeSuite(OldTextTemplateTestCase, 'test'))
    suite.addTest(unittest.makeSuite(NewTextTemplateTestCase, 'test'))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
