# -*- coding: utf-8 -*-
#
# Copyright (C) 2006 Edgewall Software
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
import unittest

from genshi.input import XML
from genshi.path import Path, PathSyntaxError


class PathTestCase(unittest.TestCase):

    def test_error_no_absolute_path(self):
        self.assertRaises(PathSyntaxError, Path, '/root')

    def test_error_unsupported_axis(self):
        self.assertRaises(PathSyntaxError, Path, '..')
        self.assertRaises(PathSyntaxError, Path, 'parent::ma')

    def test_1step(self):
        xml = XML('<root><elem/></root>')

        path = Path('elem')
        self.assertEqual('<Path "child::elem">', repr(path))
        self.assertEqual('<elem/>', path.select(xml).render())

        path = Path('child::elem')
        self.assertEqual('<Path "child::elem">', repr(path))
        self.assertEqual('<elem/>', path.select(xml).render())

        path = Path('//elem')
        self.assertEqual('<Path "descendant-or-self::node()/child::elem">',
                         repr(path))
        self.assertEqual('<elem/>', path.select(xml).render())

        path = Path('descendant::elem')
        self.assertEqual('<Path "descendant::elem">', repr(path))
        self.assertEqual('<elem/>', path.select(xml).render())

    def test_1step_self(self):
        xml = XML('<root><elem/></root>')

        path = Path('.')
        self.assertEqual('<Path "self::node()">', repr(path))
        self.assertEqual('<root><elem/></root>', path.select(xml).render())

        path = Path('self::node()')
        self.assertEqual('<Path "self::node()">', repr(path))
        self.assertEqual('<root><elem/></root>', path.select(xml).render())

    def test_1step_wildcard(self):
        xml = XML('<root><elem/></root>')

        path = Path('*')
        self.assertEqual('<Path "child::*">', repr(path))
        self.assertEqual('<elem/>', path.select(xml).render())

        path = Path('child::*')
        self.assertEqual('<Path "child::*">', repr(path))
        self.assertEqual('<elem/>', path.select(xml).render())

        path = Path('child::node()')
        self.assertEqual('<Path "child::node()">', repr(path))
        self.assertEqual('<elem/>', Path('child::node()').select(xml).render())

        path = Path('//*')
        self.assertEqual('<Path "descendant-or-self::node()/child::*">',
                         repr(path))
        self.assertEqual('<root><elem/></root>', path.select(xml).render())

    def test_1step_attribute(self):
        path = Path('@foo')
        self.assertEqual('<Path "attribute::foo">', repr(path))

        xml = XML('<root/>')
        self.assertEqual('', path.select(xml).render())

        xml = XML('<root foo="bar"/>')
        self.assertEqual('bar', path.select(xml).render())

        path = Path('./@foo')
        self.assertEqual('<Path "self::node()/attribute::foo">', repr(path))
        self.assertEqual('bar', path.select(xml).render())

    def test_1step_text(self):
        xml = XML('<root>Hey</root>')

        path = Path('text()')
        self.assertEqual('<Path "child::text()">', repr(path))
        self.assertEqual('Hey', path.select(xml).render())

        path = Path('./text()')
        self.assertEqual('<Path "self::node()/child::text()">', repr(path))
        self.assertEqual('Hey', path.select(xml).render())

        path = Path('//text()')
        self.assertEqual('<Path "descendant-or-self::node()/child::text()">',
                         repr(path))
        self.assertEqual('Hey', path.select(xml).render())

        path = Path('.//text()')
        self.assertEqual('<Path "self::node()/descendant-or-self::node()/child::text()">',
                         repr(path))
        self.assertEqual('Hey', path.select(xml).render())

    def test_2step(self):
        xml = XML('<root><foo/><bar/></root>')
        self.assertEqual('<foo/><bar/>', Path('*').select(xml).render())
        self.assertEqual('<bar/>', Path('bar').select(xml).render())
        self.assertEqual('', Path('baz').select(xml).render())

    def test_2step_attribute(self):
        xml = XML('<elem class="x"><span id="joe">Hey Joe</span></elem>')
        self.assertEqual('x', Path('@*').select(xml).render())
        self.assertEqual('x', Path('./@*').select(xml).render())
        self.assertEqual('xjoe', Path('.//@*').select(xml).render())
        self.assertEqual('joe', Path('*/@*').select(xml).render())

        xml = XML('<elem><foo id="1"/><foo id="2"/></elem>')
        self.assertEqual('', Path('@*').select(xml).render())
        self.assertEqual('12', Path('foo/@*').select(xml).render())

    def test_2step_complex(self):
        xml = XML('<root><foo><bar/></foo></root>')

        path = Path('foo/bar')
        self.assertEqual('<Path "child::foo/child::bar">', repr(path))
        self.assertEqual('<bar/>', path.select(xml).render())

        path = Path('./bar')
        self.assertEqual('<Path "self::node()/child::bar">', repr(path))
        self.assertEqual('', path.select(xml).render())

        path = Path('foo/*')
        self.assertEqual('<Path "child::foo/child::*">', repr(path))
        self.assertEqual('<bar/>', path.select(xml).render())

        xml = XML('<root><foo><bar id="1"/></foo><bar id="2"/></root>')
        path = Path('./bar')
        self.assertEqual('<Path "self::node()/child::bar">', repr(path))
        self.assertEqual('<bar id="2"/>', path.select(xml).render())

    def test_2step_text(self):
        xml = XML('<root><item>Foo</item></root>')

        path = Path('item/text()')
        self.assertEqual('<Path "child::item/child::text()">', repr(path))
        self.assertEqual('Foo', path.select(xml).render())

        path = Path('*/text()')
        self.assertEqual('<Path "child::*/child::text()">', repr(path))
        self.assertEqual('Foo', path.select(xml).render())

        path = Path('//text()')
        self.assertEqual('<Path "descendant-or-self::node()/child::text()">',
                         repr(path))
        self.assertEqual('Foo', path.select(xml).render())

        path = Path('./text()')
        self.assertEqual('<Path "self::node()/child::text()">', repr(path))
        self.assertEqual('', path.select(xml).render())

        xml = XML('<root><item>Foo</item><item>Bar</item></root>')
        path = Path('item/text()')
        self.assertEqual('<Path "child::item/child::text()">', repr(path))
        self.assertEqual('FooBar', path.select(xml).render())

        xml = XML('<root><item>Foo</item><item>Bar</item></root>')
        self.assertEqual('FooBar', path.select(xml).render())

    def test_3step(self):
        xml = XML('<root><foo><bar/></foo></root>')
        path = Path('foo/*')
        self.assertEqual('<Path "child::foo/child::*">', repr(path))
        self.assertEqual('<bar/>', path.select(xml).render())

    def test_3step_complex(self):
        xml = XML('<root><foo><bar/></foo></root>')
        path = Path('*/bar')
        self.assertEqual('<Path "child::*/child::bar">', repr(path))
        self.assertEqual('<bar/>', path.select(xml).render())

        xml = XML('<root><foo><bar id="1"/></foo><bar id="2"/></root>')
        path = Path('//bar')
        self.assertEqual('<Path "descendant-or-self::node()/child::bar">',
                         repr(path))
        self.assertEqual('<bar id="1"/><bar id="2"/>',
                         path.select(xml).render())

    def test_node_type_comment(self):
        xml = XML('<root><!-- commented --></root>')
        path = Path('comment()')
        self.assertEqual('<Path "child::comment()">', repr(path))
        self.assertEqual('<!-- commented -->', path.select(xml).render())

    def test_node_type_text(self):
        xml = XML('<root>Some text <br/>in here.</root>')
        path = Path('text()')
        self.assertEqual('<Path "child::text()">', repr(path))
        self.assertEqual('Some text in here.', path.select(xml).render())

    def test_node_type_node(self):
        xml = XML('<root>Some text <br/>in here.</root>')
        path = Path('node()')
        self.assertEqual('<Path "child::node()">', repr(path))
        self.assertEqual('Some text <br/>in here.', path.select(xml).render())

    def test_node_type_processing_instruction(self):
        xml = XML('<?python x = 2 * 3 ?><root><?php echo("x") ?></root>')

        path = Path('processing-instruction()')
        self.assertEqual('<Path "child::processing-instruction()">',
                         repr(path))
        self.assertEqual('<?python x = 2 * 3 ?><?php echo("x") ?>',
                         path.select(xml).render())

        path = Path('processing-instruction("php")')
        self.assertEqual('<Path "child::processing-instruction(\"php\")">',
                         repr(path))
        self.assertEqual('<?php echo("x") ?>', path.select(xml).render())

    def test_simple_union(self):
        xml = XML("""<body>1<br />2<br />3<br /></body>""")
        path = Path('*|text()')
        self.assertEqual('<Path "child::*|child::text()">', repr(path))
        self.assertEqual('1<br/>2<br/>3<br/>', path.select(xml).render())

    def test_predicate_name(self):
        xml = XML('<root><foo/><bar/></root>')
        path = Path('*[name()="foo"]')
        self.assertEqual('<foo/>', path.select(xml).render())

    def test_predicate_localname(self):
        xml = XML('<root><foo xmlns="NS"/><bar/></root>')
        path = Path('*[local-name()="foo"]')
        self.assertEqual('<foo xmlns="NS"/>', path.select(xml).render())

    def test_predicate_namespace(self):
        xml = XML('<root><foo xmlns="NS"/><bar/></root>')
        path = Path('*[namespace-uri()="NS"]')
        self.assertEqual('<foo xmlns="NS"/>', path.select(xml).render())

    def test_predicate_not_name(self):
        xml = XML('<root><foo/><bar/></root>')
        path = Path('*[not(name()="foo")]')
        self.assertEqual('<bar/>', path.select(xml).render())

    def test_predicate_attr(self):
        xml = XML('<root><item/><item important="very"/></root>')
        path = Path('item[@important]')
        self.assertEqual('<item important="very"/>', path.select(xml).render())
        path = Path('item[@important="very"]')
        self.assertEqual('<item important="very"/>', path.select(xml).render())

    def test_predicate_attr_equality(self):
        xml = XML('<root><item/><item important="notso"/></root>')
        path = Path('item[@important="very"]')
        self.assertEqual('', path.select(xml).render())
        path = Path('item[@important!="very"]')
        self.assertEqual('<item/><item important="notso"/>',
                         path.select(xml).render())

    def test_predicate_attr_greater_than(self):
        xml = XML('<root><item priority="3"/></root>')
        path = Path('item[@priority>3]')
        self.assertEqual('', path.select(xml).render())
        path = Path('item[@priority>2]')
        self.assertEqual('<item priority="3"/>', path.select(xml).render())

    def test_predicate_attr_less_than(self):
        xml = XML('<root><item priority="3"/></root>')
        path = Path('item[@priority<3]')
        self.assertEqual('', path.select(xml).render())
        path = Path('item[@priority<4]')
        self.assertEqual('<item priority="3"/>', path.select(xml).render())

    def test_predicate_attr_and(self):
        xml = XML('<root><item/><item important="very"/></root>')
        path = Path('item[@important and @important="very"]')
        self.assertEqual('<item important="very"/>', path.select(xml).render())
        path = Path('item[@important and @important="notso"]')
        self.assertEqual('', path.select(xml).render())

    def test_predicate_attr_or(self):
        xml = XML('<root><item/><item important="very"/></root>')
        path = Path('item[@urgent or @important]')
        self.assertEqual('<item important="very"/>', path.select(xml).render())
        path = Path('item[@urgent or @notso]')
        self.assertEqual('', path.select(xml).render())

    def test_predicate_boolean_function(self):
        xml = XML('<root><foo>bar</foo></root>')
        path = Path('*[boolean("")]')
        self.assertEqual('', path.select(xml).render())
        path = Path('*[boolean("yo")]')
        self.assertEqual('<foo>bar</foo>', path.select(xml).render())
        path = Path('*[boolean(0)]')
        self.assertEqual('', path.select(xml).render())
        path = Path('*[boolean(42)]')
        self.assertEqual('<foo>bar</foo>', path.select(xml).render())
        path = Path('*[boolean(false())]')
        self.assertEqual('', path.select(xml).render())
        path = Path('*[boolean(true())]')
        self.assertEqual('<foo>bar</foo>', path.select(xml).render())

    def test_predicate_ceil_function(self):
        xml = XML('<root><foo>bar</foo></root>')
        path = Path('*[ceiling("4.5")=5]')
        self.assertEqual('<foo>bar</foo>', path.select(xml).render())

    def test_predicate_concat_function(self):
        xml = XML('<root><foo>bar</foo></root>')
        path = Path('*[name()=concat("f", "oo")]')
        self.assertEqual('<foo>bar</foo>', path.select(xml).render())

    def test_predicate_contains_function(self):
        xml = XML('<root><foo>bar</foo></root>')
        path = Path('*[contains(name(), "oo")]')
        self.assertEqual('<foo>bar</foo>', path.select(xml).render())

    def test_predicate_matches_function(self):
        xml = XML('<root><foo>bar</foo><bar>foo</bar></root>')
        path = Path('*[matches(name(), "foo|bar")]')
        self.assertEqual('<foo>bar</foo><bar>foo</bar>', path.select(xml).render())

    def test_predicate_false_function(self):
        xml = XML('<root><foo>bar</foo></root>')
        path = Path('*[false()]')
        self.assertEqual('', path.select(xml).render())

    def test_predicate_floor_function(self):
        xml = XML('<root><foo>bar</foo></root>')
        path = Path('*[floor("4.5")=4]')
        self.assertEqual('<foo>bar</foo>', path.select(xml).render())

    def test_predicate_normalize_space_function(self):
        xml = XML('<root><foo>bar</foo></root>')
        path = Path('*[normalize-space(" foo   bar  ")="foo bar"]')
        self.assertEqual('<foo>bar</foo>', path.select(xml).render())

    def test_predicate_number_function(self):
        xml = XML('<root><foo>bar</foo></root>')
        path = Path('*[number("3.0")=3]')
        self.assertEqual('<foo>bar</foo>', path.select(xml).render())
        path = Path('*[number("3.0")=3.0]')
        self.assertEqual('<foo>bar</foo>', path.select(xml).render())
        path = Path('*[number("0.1")=.1]')
        self.assertEqual('<foo>bar</foo>', path.select(xml).render())

    def test_predicate_round_function(self):
        xml = XML('<root><foo>bar</foo></root>')
        path = Path('*[round("4.4")=4]')
        self.assertEqual('<foo>bar</foo>', path.select(xml).render())
        path = Path('*[round("4.6")=5]')
        self.assertEqual('<foo>bar</foo>', path.select(xml).render())

    def test_predicate_starts_with_function(self):
        xml = XML('<root><foo>bar</foo></root>')
        path = Path('*[starts-with(name(), "f")]')
        self.assertEqual('<foo>bar</foo>', path.select(xml).render())
        path = Path('*[starts-with(name(), "b")]')
        self.assertEqual('', path.select(xml).render())

    def test_predicate_string_length_function(self):
        xml = XML('<root><foo>bar</foo></root>')
        path = Path('*[string-length(name())=3]')
        self.assertEqual('<foo>bar</foo>', path.select(xml).render())

    def test_predicate_substring_function(self):
        xml = XML('<root><foo>bar</foo></root>')
        path = Path('*[substring(name(), 1)="oo"]')
        self.assertEqual('<foo>bar</foo>', path.select(xml).render())
        path = Path('*[substring(name(), 1, 1)="o"]')
        self.assertEqual('<foo>bar</foo>', path.select(xml).render())

    def test_predicate_substring_after_function(self):
        xml = XML('<root><foo>bar</foo></root>')
        path = Path('*[substring-after(name(), "f")="oo"]')
        self.assertEqual('<foo>bar</foo>', path.select(xml).render())

    def test_predicate_substring_before_function(self):
        xml = XML('<root><foo>bar</foo></root>')
        path = Path('*[substring-before(name(), "oo")="f"]')
        self.assertEqual('<foo>bar</foo>', path.select(xml).render())

    def test_predicate_translate_function(self):
        xml = XML('<root><foo>bar</foo></root>')
        path = Path('*[translate(name(), "fo", "ba")="baa"]')
        self.assertEqual('<foo>bar</foo>', path.select(xml).render())

    def test_predicate_true_function(self):
        xml = XML('<root><foo>bar</foo></root>')
        path = Path('*[true()]')
        self.assertEqual('<foo>bar</foo>', path.select(xml).render())

    def test_predicate_variable(self):
        xml = XML('<root><foo>bar</foo></root>')
        path = Path('*[name()=$bar]')
        variables = {'bar': 'foo'}
        self.assertEqual('<foo>bar</foo>',
                         path.select(xml, variables=variables).render())

    def test_predicate_position(self):
        xml = XML('<root><foo id="a1"/><foo id="a2"/><foo id="a3"/></root>')
        path = Path('*[2]')
        self.assertEqual('<foo id="a2"/>', path.select(xml).render())

    def test_predicate_attr_and_position(self):
        xml = XML('<root><foo/><foo id="a1"/><foo id="a2"/></root>')
        path = Path('*[@id][2]')
        self.assertEqual('<foo id="a2"/>', path.select(xml).render())

    def test_predicate_position_and_attr(self):
        xml = XML('<root><foo/><foo id="a1"/><foo id="a2"/></root>')
        path = Path('*[1][@id]')
        self.assertEqual('', path.select(xml).render())
        path = Path('*[2][@id]')
        self.assertEqual('<foo id="a1"/>', path.select(xml).render())

    def test_name_with_namespace(self):
        xml = XML('<root xmlns:f="FOO"><f:foo>bar</f:foo></root>')
        path = Path('f:foo')
        self.assertEqual('<Path "child::f:foo">', repr(path))
        namespaces = {'f': 'FOO'}
        self.assertEqual('<foo xmlns="FOO">bar</foo>',
                         path.select(xml, namespaces=namespaces).render())

    def test_wildcard_with_namespace(self):
        xml = XML('<root xmlns:f="FOO"><f:foo>bar</f:foo></root>')
        path = Path('f:*')
        self.assertEqual('<Path "child::f:*">', repr(path))
        namespaces = {'f': 'FOO'}
        self.assertEqual('<foo xmlns="FOO">bar</foo>',
                         path.select(xml, namespaces=namespaces).render())

    def test_predicate_termination(self):
        """
        Verify that a patch matching the self axis with a predicate doesn't
        cause an infinite loop. See <http://genshi.edgewall.org/ticket/82>.
        """
        xml = XML('<ul flag="1"><li>a</li><li>b</li></ul>')
        path = Path('.[@flag="1"]/*')
        self.assertEqual('<li>a</li><li>b</li>', path.select(xml).render())

        xml = XML('<ul flag="1"><li>a</li><li>b</li></ul>')
        path = Path('.[@flag="0"]/*')
        self.assertEqual('', path.select(xml).render())

    def test_attrname_with_namespace(self):
        xml = XML('<root xmlns:f="FOO"><foo f:bar="baz"/></root>')
        path = Path('foo[@f:bar]')
        self.assertEqual('<foo xmlns:ns1="FOO" ns1:bar="baz"/>',
                         path.select(xml, namespaces={'f': 'FOO'}).render())

    def test_attrwildcard_with_namespace(self):
        xml = XML('<root xmlns:f="FOO"><foo f:bar="baz"/></root>')
        path = Path('foo[@f:*]')
        self.assertEqual('<foo xmlns:ns1="FOO" ns1:bar="baz"/>',
                         path.select(xml, namespaces={'f': 'FOO'}).render())


def suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite(Path.__module__))
    suite.addTest(unittest.makeSuite(PathTestCase, 'test'))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
