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

from genshi.core import TEXT
from genshi.template.loader import TemplateLoader
from genshi.template.markup import MarkupTemplate


class TemplateLoaderTestCase(unittest.TestCase):
    """Tests for the template loader."""

    def setUp(self):
        self.dirname = tempfile.mkdtemp(suffix='markup_test')

    def tearDown(self):
        shutil.rmtree(self.dirname)

    def test_search_path_empty(self):
        loader = TemplateLoader()
        self.assertEqual([], loader.search_path)

    def test_search_path_as_string(self):
        loader = TemplateLoader(self.dirname)
        self.assertEqual([self.dirname], loader.search_path)

    def test_relative_include_samedir(self):
        file1 = open(os.path.join(self.dirname, 'tmpl1.html'), 'w')
        try:
            file1.write("""<div>Included</div>""")
        finally:
            file1.close()

        file2 = open(os.path.join(self.dirname, 'tmpl2.html'), 'w')
        try:
            file2.write("""<html xmlns:xi="http://www.w3.org/2001/XInclude">
              <xi:include href="tmpl1.html" />
            </html>""")
        finally:
            file2.close()

        loader = TemplateLoader([self.dirname])
        tmpl = loader.load('tmpl2.html')
        self.assertEqual("""<html>
              <div>Included</div>
            </html>""", tmpl.generate().render())

    def test_relative_include_subdir(self):
        os.mkdir(os.path.join(self.dirname, 'sub'))
        file1 = open(os.path.join(self.dirname, 'sub', 'tmpl1.html'), 'w')
        try:
            file1.write("""<div>Included</div>""")
        finally:
            file1.close()

        file2 = open(os.path.join(self.dirname, 'tmpl2.html'), 'w')
        try:
            file2.write("""<html xmlns:xi="http://www.w3.org/2001/XInclude">
              <xi:include href="sub/tmpl1.html" />
            </html>""")
        finally:
            file2.close()

        loader = TemplateLoader([self.dirname])
        tmpl = loader.load('tmpl2.html')
        self.assertEqual("""<html>
              <div>Included</div>
            </html>""", tmpl.generate().render())

    def test_relative_include_parentdir(self):
        file1 = open(os.path.join(self.dirname, 'tmpl1.html'), 'w')
        try:
            file1.write("""<div>Included</div>""")
        finally:
            file1.close()

        os.mkdir(os.path.join(self.dirname, 'sub'))
        file2 = open(os.path.join(self.dirname, 'sub', 'tmpl2.html'), 'w')
        try:
            file2.write("""<html xmlns:xi="http://www.w3.org/2001/XInclude">
              <xi:include href="../tmpl1.html" />
            </html>""")
        finally:
            file2.close()

        loader = TemplateLoader([self.dirname])
        tmpl = loader.load('sub/tmpl2.html')
        self.assertEqual("""<html>
              <div>Included</div>
            </html>""", tmpl.generate().render())

    def test_relative_include_samesubdir(self):
        file1 = open(os.path.join(self.dirname, 'tmpl1.html'), 'w')
        try:
            file1.write("""<div>Included tmpl1.html</div>""")
        finally:
            file1.close()

        os.mkdir(os.path.join(self.dirname, 'sub'))
        file2 = open(os.path.join(self.dirname, 'sub', 'tmpl1.html'), 'w')
        try:
            file2.write("""<div>Included sub/tmpl1.html</div>""")
        finally:
            file2.close()

        file3 = open(os.path.join(self.dirname, 'sub', 'tmpl2.html'), 'w')
        try:
            file3.write("""<html xmlns:xi="http://www.w3.org/2001/XInclude">
              <xi:include href="tmpl1.html" />
            </html>""")
        finally:
            file3.close()

        loader = TemplateLoader([self.dirname])
        tmpl = loader.load('sub/tmpl2.html')
        self.assertEqual("""<html>
              <div>Included sub/tmpl1.html</div>
            </html>""", tmpl.generate().render())

    def test_relative_include_without_search_path(self):
        file1 = open(os.path.join(self.dirname, 'tmpl1.html'), 'w')
        try:
            file1.write("""<div>Included</div>""")
        finally:
            file1.close()

        file2 = open(os.path.join(self.dirname, 'tmpl2.html'), 'w')
        try:
            file2.write("""<html xmlns:xi="http://www.w3.org/2001/XInclude">
              <xi:include href="tmpl1.html" />
            </html>""")
        finally:
            file2.close()

        loader = TemplateLoader()
        tmpl = loader.load(os.path.join(self.dirname, 'tmpl2.html'))
        self.assertEqual("""<html>
              <div>Included</div>
            </html>""", tmpl.generate().render())

    def test_relative_include_without_search_path_nested(self):
        file1 = open(os.path.join(self.dirname, 'tmpl1.html'), 'w')
        try:
            file1.write("""<div>Included</div>""")
        finally:
            file1.close()

        file2 = open(os.path.join(self.dirname, 'tmpl2.html'), 'w')
        try:
            file2.write("""<div xmlns:xi="http://www.w3.org/2001/XInclude">
              <xi:include href="tmpl1.html" />
            </div>""")
        finally:
            file2.close()

        file3 = open(os.path.join(self.dirname, 'tmpl3.html'), 'w')
        try:
            file3.write("""<html xmlns:xi="http://www.w3.org/2001/XInclude">
              <xi:include href="tmpl2.html" />
            </html>""")
        finally:
            file3.close()

        loader = TemplateLoader()
        tmpl = loader.load(os.path.join(self.dirname, 'tmpl3.html'))
        self.assertEqual("""<html>
              <div>
              <div>Included</div>
            </div>
            </html>""", tmpl.generate().render())

    def test_relative_include_from_inmemory_template(self):
        file1 = open(os.path.join(self.dirname, 'tmpl1.html'), 'w')
        try:
            file1.write("""<div>Included</div>""")
        finally:
            file1.close()

        loader = TemplateLoader([self.dirname])
        tmpl2 = MarkupTemplate("""<html xmlns:xi="http://www.w3.org/2001/XInclude">
          <xi:include href="../tmpl1.html" />
        </html>""", filename='subdir/tmpl2.html', loader=loader)

        self.assertEqual("""<html>
          <div>Included</div>
        </html>""", tmpl2.generate().render())

    def test_relative_absolute_template_preferred(self):
        file1 = open(os.path.join(self.dirname, 'tmpl1.html'), 'w')
        try:
            file1.write("""<div>Included</div>""")
        finally:
            file1.close()

        os.mkdir(os.path.join(self.dirname, 'sub'))
        file2 = open(os.path.join(self.dirname, 'sub', 'tmpl1.html'), 'w')
        try:
            file2.write("""<div>Included from sub</div>""")
        finally:
            file2.close()

        file3 = open(os.path.join(self.dirname, 'sub', 'tmpl2.html'), 'w')
        try:
            file3.write("""<html xmlns:xi="http://www.w3.org/2001/XInclude">
              <xi:include href="tmpl1.html" />
            </html>""")
        finally:
            file3.close()

        loader = TemplateLoader()
        tmpl = loader.load(os.path.abspath(os.path.join(self.dirname, 'sub',
                                                        'tmpl2.html')))
        self.assertEqual("""<html>
              <div>Included from sub</div>
            </html>""", tmpl.generate().render())

    def test_abspath_caching(self):
        abspath = os.path.join(self.dirname, 'abs')
        os.mkdir(abspath)
        file1 = open(os.path.join(abspath, 'tmpl1.html'), 'w')
        try:
            file1.write("""<html xmlns:xi="http://www.w3.org/2001/XInclude">
              <xi:include href="tmpl2.html" />
            </html>""")
        finally:
            file1.close()

        file2 = open(os.path.join(abspath, 'tmpl2.html'), 'w')
        try:
            file2.write("""<div>Included from abspath.</div>""")
        finally:
            file2.close()

        searchpath = os.path.join(self.dirname, 'searchpath')
        os.mkdir(searchpath)
        file3 = open(os.path.join(searchpath, 'tmpl2.html'), 'w')
        try:
            file3.write("""<div>Included from searchpath.</div>""")
        finally:
            file3.close()

        loader = TemplateLoader(searchpath)
        tmpl1 = loader.load(os.path.join(abspath, 'tmpl1.html'))
        self.assertEqual("""<html>
              <div>Included from searchpath.</div>
            </html>""", tmpl1.generate().render())
        assert 'tmpl2.html' in loader._cache

    def test_abspath_include_caching_without_search_path(self):
        file1 = open(os.path.join(self.dirname, 'tmpl1.html'), 'w')
        try:
            file1.write("""<html xmlns:xi="http://www.w3.org/2001/XInclude">
              <xi:include href="tmpl2.html" />
            </html>""")
        finally:
            file1.close()

        file2 = open(os.path.join(self.dirname, 'tmpl2.html'), 'w')
        try:
            file2.write("""<div>Included</div>""")
        finally:
            file2.close()

        os.mkdir(os.path.join(self.dirname, 'sub'))
        file3 = open(os.path.join(self.dirname, 'sub', 'tmpl1.html'), 'w')
        try:
            file3.write("""<html xmlns:xi="http://www.w3.org/2001/XInclude">
              <xi:include href="tmpl2.html" />
            </html>""")
        finally:
            file3.close()

        file4 = open(os.path.join(self.dirname, 'sub', 'tmpl2.html'), 'w')
        try:
            file4.write("""<div>Included from sub</div>""")
        finally:
            file4.close()

        loader = TemplateLoader()
        tmpl1 = loader.load(os.path.join(self.dirname, 'tmpl1.html'))
        self.assertEqual("""<html>
              <div>Included</div>
            </html>""", tmpl1.generate().render())
        tmpl2 = loader.load(os.path.join(self.dirname, 'sub', 'tmpl1.html'))
        self.assertEqual("""<html>
              <div>Included from sub</div>
            </html>""", tmpl2.generate().render())
        assert 'tmpl2.html' not in loader._cache

    def test_load_with_default_encoding(self):
        f = open(os.path.join(self.dirname, 'tmpl.html'), 'w')
        try:
            f.write(u'<div>\xf6</div>'.encode('iso-8859-1'))
        finally:
            f.close()
        loader = TemplateLoader([self.dirname], default_encoding='iso-8859-1')
        loader.load('tmpl.html')

    def test_load_with_explicit_encoding(self):
        f = open(os.path.join(self.dirname, 'tmpl.html'), 'w')
        try:
            f.write(u'<div>\xf6</div>'.encode('iso-8859-1'))
        finally:
            f.close()
        loader = TemplateLoader([self.dirname], default_encoding='utf-8')
        loader.load('tmpl.html', encoding='iso-8859-1')

    def test_load_with_callback(self):
        fileobj = open(os.path.join(self.dirname, 'tmpl.html'), 'w')
        try:
            fileobj.write("""<html>
              <p>Hello</p>
            </html>""")
        finally:
            fileobj.close()

        def template_loaded(template):
            def my_filter(stream, ctxt):
                for kind, data, pos in stream:
                    if kind is TEXT and data.strip():
                        data = ', '.join([data, data.lower()])
                    yield kind, data, pos
            template.filters.insert(0, my_filter)

        loader = TemplateLoader([self.dirname], callback=template_loaded)
        tmpl = loader.load('tmpl.html')
        self.assertEqual("""<html>
              <p>Hello, hello</p>
            </html>""", tmpl.generate().render())

        # Make sure the filter is only added once
        tmpl = loader.load('tmpl.html')
        self.assertEqual("""<html>
              <p>Hello, hello</p>
            </html>""", tmpl.generate().render())

    def test_prefix_delegation_to_directories(self):
        """
        Test prefix delegation with the following layout:
        
        templates/foo.html
        sub1/templates/tmpl1.html
        sub2/templates/tmpl2.html
        
        Where sub1 and sub2 are prefixes, and both tmpl1.html and tmpl2.html
        incldue foo.html.
        """
        dir1 = os.path.join(self.dirname, 'templates')
        os.mkdir(dir1)
        file1 = open(os.path.join(dir1, 'foo.html'), 'w')
        try:
            file1.write("""<div>Included foo</div>""")
        finally:
            file1.close()

        dir2 = os.path.join(self.dirname, 'sub1', 'templates')
        os.makedirs(dir2)
        file2 = open(os.path.join(dir2, 'tmpl1.html'), 'w')
        try:
            file2.write("""<html xmlns:xi="http://www.w3.org/2001/XInclude">
              <xi:include href="../foo.html" /> from sub1
            </html>""")
        finally:
            file2.close()

        dir3 = os.path.join(self.dirname, 'sub2', 'templates')
        os.makedirs(dir3)
        file3 = open(os.path.join(dir3, 'tmpl2.html'), 'w')
        try:
            file3.write("""<div>tmpl2</div>""")
        finally:
            file3.close()

        loader = TemplateLoader([dir1, TemplateLoader.prefixed(
            sub1 = dir2,
            sub2 = dir3
        )])
        tmpl = loader.load('sub1/tmpl1.html')
        self.assertEqual("""<html>
              <div>Included foo</div> from sub1
            </html>""", tmpl.generate().render())

    def test_prefix_delegation_to_directories_with_subdirs(self):
        """
        Test prefix delegation with the following layout:
        
        templates/foo.html
        sub1/templates/tmpl1.html
        sub1/templates/tmpl2.html
        sub1/templates/bar/tmpl3.html
        
        Where sub1 is a prefix, and tmpl1.html includes all the others.
        """
        dir1 = os.path.join(self.dirname, 'templates')
        os.mkdir(dir1)
        file1 = open(os.path.join(dir1, 'foo.html'), 'w')
        try:
            file1.write("""<div>Included foo</div>""")
        finally:
            file1.close()

        dir2 = os.path.join(self.dirname, 'sub1', 'templates')
        os.makedirs(dir2)
        file2 = open(os.path.join(dir2, 'tmpl1.html'), 'w')
        try:
            file2.write("""<html xmlns:xi="http://www.w3.org/2001/XInclude">
              <xi:include href="../foo.html" /> from sub1
              <xi:include href="tmpl2.html" /> from sub1
              <xi:include href="bar/tmpl3.html" /> from sub1
            </html>""")
        finally:
            file2.close()

        file3 = open(os.path.join(dir2, 'tmpl2.html'), 'w')
        try:
            file3.write("""<div>tmpl2</div>""")
        finally:
            file3.close()

        dir3 = os.path.join(self.dirname, 'sub1', 'templates', 'bar')
        os.makedirs(dir3)
        file4 = open(os.path.join(dir3, 'tmpl3.html'), 'w')
        try:
            file4.write("""<div>bar/tmpl3</div>""")
        finally:
            file4.close()

        loader = TemplateLoader([dir1, TemplateLoader.prefixed(
            sub1 = os.path.join(dir2),
            sub2 = os.path.join(dir3)
        )])
        tmpl = loader.load('sub1/tmpl1.html')
        self.assertEqual("""<html>
              <div>Included foo</div> from sub1
              <div>tmpl2</div> from sub1
              <div>bar/tmpl3</div> from sub1
            </html>""", tmpl.generate().render())


def suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite(TemplateLoader.__module__))
    suite.addTest(unittest.makeSuite(TemplateLoaderTestCase, 'test'))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
