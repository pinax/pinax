# -*- coding: utf-8 -*-
#
# Copyright (C) 2006-2007 Edgewall Software
# Copyright (C) 2006 Matthew Good
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
import unittest

from genshi.core import Stream
from genshi.output import DocType
from genshi.template import MarkupTemplate, TextTemplate, NewTextTemplate
from genshi.template.plugin import ConfigurationError, \
                                   MarkupTemplateEnginePlugin, \
                                   TextTemplateEnginePlugin

PACKAGE = 'genshi.template.tests'


class MarkupTemplateEnginePluginTestCase(unittest.TestCase):

    def test_init_no_options(self):
        plugin = MarkupTemplateEnginePlugin()
        self.assertEqual('utf-8', plugin.default_encoding)
        self.assertEqual('html', plugin.default_format)
        self.assertEqual(None, plugin.default_doctype)

        self.assertEqual([], plugin.loader.search_path)
        self.assertEqual(True, plugin.loader.auto_reload)
        self.assertEqual(25, plugin.loader._cache.capacity)

    def test_init_with_loader_options(self):
        plugin = MarkupTemplateEnginePlugin(options={
            'genshi.auto_reload': 'off',
            'genshi.max_cache_size': '100',
            'genshi.search_path': '/usr/share/tmpl:/usr/local/share/tmpl',
        })
        self.assertEqual(['/usr/share/tmpl', '/usr/local/share/tmpl'],
                         plugin.loader.search_path)
        self.assertEqual(False, plugin.loader.auto_reload)
        self.assertEqual(100, plugin.loader._cache.capacity)

    def test_init_with_invalid_cache_size(self):
        self.assertRaises(ConfigurationError, MarkupTemplateEnginePlugin,
                          options={'genshi.max_cache_size': 'thirty'})

    def test_init_with_output_options(self):
        plugin = MarkupTemplateEnginePlugin(options={
            'genshi.default_encoding': 'iso-8859-15',
            'genshi.default_format': 'xhtml',
            'genshi.default_doctype': 'xhtml-strict',
        })
        self.assertEqual('iso-8859-15', plugin.default_encoding)
        self.assertEqual('xhtml', plugin.default_format)
        self.assertEqual(DocType.XHTML, plugin.default_doctype)

    def test_init_with_invalid_output_format(self):
        self.assertRaises(ConfigurationError, MarkupTemplateEnginePlugin,
                          options={'genshi.default_format': 'foobar'})

    def test_init_with_invalid_doctype(self):
        self.assertRaises(ConfigurationError, MarkupTemplateEnginePlugin,
                          options={'genshi.default_doctype': 'foobar'})

    def test_load_template_from_file(self):
        plugin = MarkupTemplateEnginePlugin()
        tmpl = plugin.load_template(PACKAGE + '.templates.test')
        self.assertEqual('test.html', os.path.basename(tmpl.filename))
        assert isinstance(tmpl, MarkupTemplate)

    def test_load_template_from_string(self):
        plugin = MarkupTemplateEnginePlugin()
        tmpl = plugin.load_template(None, template_string="""<p>
          $message
        </p>""")
        self.assertEqual(None, tmpl.filename)
        assert isinstance(tmpl, MarkupTemplate)

    def test_transform_with_load(self):
        plugin = MarkupTemplateEnginePlugin()
        tmpl = plugin.load_template(PACKAGE + '.templates.test')
        stream = plugin.transform({'message': 'Hello'}, tmpl)
        assert isinstance(stream, Stream)

    def test_transform_without_load(self):
        plugin = MarkupTemplateEnginePlugin()
        stream = plugin.transform({'message': 'Hello'},
                                  PACKAGE + '.templates.test')
        assert isinstance(stream, Stream)

    def test_render(self):
        plugin = MarkupTemplateEnginePlugin()
        tmpl = plugin.load_template(PACKAGE + '.templates.test')
        output = plugin.render({'message': 'Hello'}, template=tmpl)
        self.assertEqual("""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html lang="en">
  <head>
    <title>Test</title>
  </head>
  <body>
    <h1>Test</h1>
    <p>Hello</p>
  </body>
</html>""", output)

    def test_render_with_format(self):
        plugin = MarkupTemplateEnginePlugin()
        tmpl = plugin.load_template(PACKAGE + '.templates.test')
        output = plugin.render({'message': 'Hello'}, format='xhtml',
                               template=tmpl)
        self.assertEqual("""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en">
  <head>
    <title>Test</title>
  </head>
  <body>
    <h1>Test</h1>
    <p>Hello</p>
  </body>
</html>""", output)

    def test_render_with_doctype(self):
        plugin = MarkupTemplateEnginePlugin(options={
            'genshi.default_doctype': 'html-strict',
        })
        tmpl = plugin.load_template(PACKAGE + '.templates.test')
        output = plugin.render({'message': 'Hello'}, template=tmpl)
        self.assertEqual("""<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html lang="en">
  <head>
    <title>Test</title>
  </head>
  <body>
    <h1>Test</h1>
    <p>Hello</p>
  </body>
</html>""", output)

    def test_render_fragment_with_doctype(self):
        plugin = MarkupTemplateEnginePlugin(options={
            'genshi.default_doctype': 'html-strict',
        })
        tmpl = plugin.load_template(PACKAGE + '.templates.test_no_doctype')
        output = plugin.render({'message': 'Hello'}, template=tmpl,
                               fragment=True)
        self.assertEqual("""<html lang="en">
  <head>
    <title>Test</title>
  </head>
  <body>
    <h1>Test</h1>
    <p>Hello</p>
  </body>
</html>""", output)

    def test_helper_functions(self):
        plugin = MarkupTemplateEnginePlugin()
        tmpl = plugin.load_template(PACKAGE + '.templates.functions')
        output = plugin.render({'snippet': '<b>Foo</b>'}, template=tmpl)
        self.assertEqual("""<div>
False
bar
<b>Foo</b>
<b>Foo</b>
</div>""", output)


class TextTemplateEnginePluginTestCase(unittest.TestCase):

    def test_init_no_options(self):
        plugin = TextTemplateEnginePlugin()
        self.assertEqual('utf-8', plugin.default_encoding)
        self.assertEqual('text', plugin.default_format)

        self.assertEqual([], plugin.loader.search_path)
        self.assertEqual(True, plugin.loader.auto_reload)
        self.assertEqual(25, plugin.loader._cache.capacity)

    def test_init_with_loader_options(self):
        plugin = TextTemplateEnginePlugin(options={
            'genshi.auto_reload': 'off',
            'genshi.max_cache_size': '100',
            'genshi.search_path': '/usr/share/tmpl:/usr/local/share/tmpl',
        })
        self.assertEqual(['/usr/share/tmpl', '/usr/local/share/tmpl'],
                         plugin.loader.search_path)
        self.assertEqual(False, plugin.loader.auto_reload)
        self.assertEqual(100, plugin.loader._cache.capacity)

    def test_init_with_output_options(self):
        plugin = TextTemplateEnginePlugin(options={
            'genshi.default_encoding': 'iso-8859-15',
        })
        self.assertEqual('iso-8859-15', plugin.default_encoding)

    def test_init_with_new_syntax(self):
        plugin = TextTemplateEnginePlugin(options={
            'genshi.new_text_syntax': 'yes',
        })
        self.assertEqual(NewTextTemplate, plugin.template_class)
        tmpl = plugin.load_template(PACKAGE + '.templates.new_syntax')
        output = plugin.render({'foo': True}, template=tmpl)
        self.assertEqual('bar', output)

    def test_load_template_from_file(self):
        plugin = TextTemplateEnginePlugin()
        tmpl = plugin.load_template(PACKAGE + '.templates.test')
        assert isinstance(tmpl, TextTemplate)
        self.assertEqual('test.txt', os.path.basename(tmpl.filename))

    def test_load_template_from_string(self):
        plugin = TextTemplateEnginePlugin()
        tmpl = plugin.load_template(None, template_string="$message")
        self.assertEqual(None, tmpl.filename)
        assert isinstance(tmpl, TextTemplate)

    def test_transform_without_load(self):
        plugin = TextTemplateEnginePlugin()
        stream = plugin.transform({'message': 'Hello'},
                                  PACKAGE + '.templates.test')
        assert isinstance(stream, Stream)

    def test_transform_with_load(self):
        plugin = TextTemplateEnginePlugin()
        tmpl = plugin.load_template(PACKAGE + '.templates.test')
        stream = plugin.transform({'message': 'Hello'}, tmpl)
        assert isinstance(stream, Stream)

    def test_render(self):
        plugin = TextTemplateEnginePlugin()
        tmpl = plugin.load_template(PACKAGE + '.templates.test')
        output = plugin.render({'message': 'Hello'}, template=tmpl)
        self.assertEqual("""Test
====

Hello
""", output)

    def test_helper_functions(self):
        plugin = TextTemplateEnginePlugin()
        tmpl = plugin.load_template(PACKAGE + '.templates.functions')
        output = plugin.render({}, template=tmpl)
        self.assertEqual("""False
bar
""", output)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(MarkupTemplateEnginePluginTestCase, 'test'))
    suite.addTest(unittest.makeSuite(TextTemplateEnginePluginTestCase, 'test'))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
