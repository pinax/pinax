# -*- coding: utf-8 -*-
#
# Copyright (C) 2007 Edgewall Software
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
from pprint import pprint
import unittest

from genshi import HTML
from genshi.builder import Element
from genshi.core import START, END, TEXT, QName, Attrs
from genshi.filters.transform import Transformer, StreamBuffer, ENTER, EXIT, \
                                     OUTSIDE, INSIDE, ATTR, BREAK
import genshi.filters.transform


FOO = '<root>ROOT<foo name="foo">FOO</foo></root>'
FOOBAR = '<root>ROOT<foo name="foo" size="100">FOO</foo><bar name="bar">BAR</bar></root>'


def _simplify(stream, with_attrs=False):
    """Simplify a marked stream."""
    def _generate():
        for mark, (kind, data, pos) in stream:
            if kind is START:
                if with_attrs:
                    data = (unicode(data[0]), dict([(unicode(k), v)
                                                    for k, v in data[1]]))
                else:
                    data = unicode(data[0])
            elif kind is END:
                data = unicode(data)
            elif kind is ATTR:
                kind = ATTR
                data = dict([(unicode(k), v) for k, v in data[1]])
            yield mark, kind, data
    return list(_generate())


def _transform(html, transformer, with_attrs=False):
    """Apply transformation returning simplified marked stream."""
    if isinstance(html, basestring):
        html = HTML(html)
    stream = transformer(html, keep_marks=True)
    return _simplify(stream, with_attrs)


class SelectTest(unittest.TestCase):
    """Test .select()"""
    def _select(self, select):
        html = HTML(FOOBAR)
        if isinstance(select, basestring):
            select = [select]
        transformer = Transformer(select[0])
        for sel in select[1:]:
            transformer = transformer.select(sel)
        return _transform(html, transformer)

    def test_select_single_element(self):
        self.assertEqual(
            self._select('foo'),
            [(None, START, u'root'),
             (None, TEXT, u'ROOT'),
             (ENTER, START, u'foo'),
             (INSIDE, TEXT, u'FOO'),
             (EXIT, END, u'foo'),
             (None, START, u'bar'),
             (None, TEXT, u'BAR'),
             (None, END, u'bar'),
             (None, END, u'root')],
            )

    def test_select_context(self):
        self.assertEqual(
            self._select('.'),
            [(ENTER, START, u'root'),
             (INSIDE, TEXT, u'ROOT'),
             (INSIDE, START, u'foo'),
             (INSIDE, TEXT, u'FOO'),
             (INSIDE, END, u'foo'),
             (INSIDE, START, u'bar'),
             (INSIDE, TEXT, u'BAR'),
             (INSIDE, END, u'bar'),
             (EXIT, END, u'root')]
            )

    def test_select_inside_select(self):
        self.assertEqual(
            self._select(['.', 'foo']),
            [(None, START, u'root'),
             (None, TEXT, u'ROOT'),
             (ENTER, START, u'foo'),
             (INSIDE, TEXT, u'FOO'),
             (EXIT, END, u'foo'),
             (None, START, u'bar'),
             (None, TEXT, u'BAR'),
             (None, END, u'bar'),
             (None, END, u'root')],
            )

    def test_select_text(self):
        self.assertEqual(
            self._select('*/text()'),
            [(None, START, u'root'),
             (None, TEXT, u'ROOT'),
             (None, START, u'foo'),
             (OUTSIDE, TEXT, u'FOO'),
             (None, END, u'foo'),
             (None, START, u'bar'),
             (OUTSIDE, TEXT, u'BAR'),
             (None, END, u'bar'),
             (None, END, u'root')],
            )

    def test_select_attr(self):
        self.assertEqual(
            self._select('foo/@name'),
            [(None, START, u'root'),
             (None, TEXT, u'ROOT'),
             (ATTR, ATTR, {'name': u'foo'}),
             (None, START, u'foo'),
             (None, TEXT, u'FOO'),
             (None, END, u'foo'),
             (None, START, u'bar'),
             (None, TEXT, u'BAR'),
             (None, END, u'bar'),
             (None, END, u'root')]
            )

    def test_select_text_context(self):
        self.assertEqual(
            list(Transformer('.')(HTML('foo'), keep_marks=True)),
            [('OUTSIDE', ('TEXT', u'foo', (None, 1, 0)))],
            )


class InvertTest(unittest.TestCase):
    def _invert(self, select):
        return _transform(FOO, Transformer(select).invert())

    def test_invert_element(self):
        self.assertEqual(
            self._invert('foo'),
            [(OUTSIDE, START, u'root'),
             (OUTSIDE, TEXT, u'ROOT'),
             (None, START, u'foo'),
             (None, TEXT, u'FOO'),
             (None, END, u'foo'),
             (OUTSIDE, END, u'root')]
            )

    def test_invert_inverted_element(self):
        self.assertEqual(
            _transform(FOO, Transformer('foo').invert().invert()),
            [(None, START, u'root'),
             (None, TEXT, u'ROOT'),
             (OUTSIDE, START, u'foo'),
             (OUTSIDE, TEXT, u'FOO'),
             (OUTSIDE, END, u'foo'),
             (None, END, u'root')]
            )

    def test_invert_text(self):
        self.assertEqual(
            self._invert('foo/text()'),
            [(OUTSIDE, START, u'root'),
             (OUTSIDE, TEXT, u'ROOT'),
             (OUTSIDE, START, u'foo'),
             (None, TEXT, u'FOO'),
             (OUTSIDE, END, u'foo'),
             (OUTSIDE, END, u'root')]
            )

    def test_invert_attribute(self):
        self.assertEqual(
            self._invert('foo/@name'),
            [(OUTSIDE, START, u'root'),
             (OUTSIDE, TEXT, u'ROOT'),
             (None, ATTR, {'name': u'foo'}),
             (OUTSIDE, START, u'foo'),
             (OUTSIDE, TEXT, u'FOO'),
             (OUTSIDE, END, u'foo'),
             (OUTSIDE, END, u'root')]
            )

    def test_invert_context(self):
        self.assertEqual(
            self._invert('.'),
            [(None, START, u'root'),
             (None, TEXT, u'ROOT'),
             (None, START, u'foo'),
             (None, TEXT, u'FOO'),
             (None, END, u'foo'),
             (None, END, u'root')]
            )

    def test_invert_text_context(self):
        self.assertEqual(
            _simplify(Transformer('.').invert()(HTML('foo'), keep_marks=True)),
            [(None, 'TEXT', u'foo')],
            )



class EndTest(unittest.TestCase):
    def test_end(self):
        stream = _transform(FOO, Transformer('foo').end())
        self.assertEqual(
            stream,
            [(OUTSIDE, START, u'root'),
             (OUTSIDE, TEXT, u'ROOT'),
             (OUTSIDE, START, u'foo'),
             (OUTSIDE, TEXT, u'FOO'),
             (OUTSIDE, END, u'foo'),
             (OUTSIDE, END, u'root')]
            )


class EmptyTest(unittest.TestCase):
    def _empty(self, select):
        return _transform(FOO, Transformer(select).empty())

    def test_empty_element(self):
        self.assertEqual(
            self._empty('foo'),
            [(None, START, u'root'),
             (None, TEXT, u'ROOT'),
             (ENTER, START, u'foo'),
             (EXIT, END, u'foo'),
             (None, END, u'root')],
            )

    def test_empty_text(self):
        self.assertEqual(
            self._empty('foo/text()'),
            [(None, START, u'root'),
             (None, TEXT, u'ROOT'),
             (None, START, u'foo'),
             (OUTSIDE, TEXT, u'FOO'),
             (None, END, u'foo'),
             (None, END, u'root')]
            )

    def test_empty_attr(self):
        self.assertEqual(
            self._empty('foo/@name'),
            [(None, START, u'root'),
             (None, TEXT, u'ROOT'),
             (ATTR, ATTR, {'name': u'foo'}),
             (None, START, u'foo'),
             (None, TEXT, u'FOO'),
             (None, END, u'foo'),
             (None, END, u'root')]
            )

    def test_empty_context(self):
        self.assertEqual(
            self._empty('.'),
            [(ENTER, START, u'root'),
             (EXIT, END, u'root')]
            )

    def test_empty_text_context(self):
        self.assertEqual(
            _simplify(Transformer('.')(HTML('foo'), keep_marks=True)),
            [(OUTSIDE, TEXT, u'foo')],
            )


class RemoveTest(unittest.TestCase):
    def _remove(self, select):
        return _transform(FOO, Transformer(select).remove())

    def test_remove_element(self):
        self.assertEqual(
            self._remove('foo|bar'),
            [(None, START, u'root'),
             (None, TEXT, u'ROOT'),
             (None, END, u'root')]
            )

    def test_remove_text(self):
        self.assertEqual(
            self._remove('//text()'),
            [(None, START, u'root'),
             (None, START, u'foo'),
             (None, END, u'foo'),
             (None, END, u'root')]
            )

    def test_remove_attr(self):
        self.assertEqual(
            self._remove('foo/@name'),
            [(None, START, u'root'),
             (None, TEXT, u'ROOT'),
             (None, START, u'foo'),
             (None, TEXT, u'FOO'),
             (None, END, u'foo'),
             (None, END, u'root')]
            )

    def test_remove_context(self):
        self.assertEqual(
            self._remove('.'),
            [],
            )

    def test_remove_text_context(self):
        self.assertEqual(
            _transform('foo', Transformer('.').remove()),
            [],
            )


class UnwrapText(unittest.TestCase):
    def _unwrap(self, select):
        return _transform(FOO, Transformer(select).unwrap())

    def test_unwrap_element(self):
        self.assertEqual(
            self._unwrap('foo'),
            [(None, START, u'root'),
             (None, TEXT, u'ROOT'),
             (INSIDE, TEXT, u'FOO'),
             (None, END, u'root')]
            )

    def test_unwrap_text(self):
        self.assertEqual(
            self._unwrap('foo/text()'),
            [(None, START, u'root'),
             (None, TEXT, u'ROOT'),
             (None, START, u'foo'),
             (OUTSIDE, TEXT, u'FOO'),
             (None, END, u'foo'),
             (None, END, u'root')]
            )

    def test_unwrap_attr(self):
        self.assertEqual(
            self._unwrap('foo/@name'),
            [(None, START, u'root'),
             (None, TEXT, u'ROOT'),
             (ATTR, ATTR, {'name': u'foo'}),
             (None, START, u'foo'),
             (None, TEXT, u'FOO'),
             (None, END, u'foo'),
             (None, END, u'root')]
            )

    def test_unwrap_adjacent(self):
        self.assertEqual(
            _transform(FOOBAR, Transformer('foo|bar').unwrap()),
            [(None, START, u'root'),
             (None, TEXT, u'ROOT'),
             (INSIDE, TEXT, u'FOO'),
             (INSIDE, TEXT, u'BAR'),
             (None, END, u'root')]
            )

    def test_unwrap_root(self):
        self.assertEqual(
            self._unwrap('.'),
            [(INSIDE, TEXT, u'ROOT'),
             (INSIDE, START, u'foo'),
             (INSIDE, TEXT, u'FOO'),
             (INSIDE, END, u'foo')]
            )

    def test_unwrap_text_root(self):
        self.assertEqual(
            _transform('foo', Transformer('.').unwrap()),
            [(OUTSIDE, TEXT, 'foo')],
            )


class WrapTest(unittest.TestCase):
    def _wrap(self, select, wrap='wrap'):
        return _transform(FOO, Transformer(select).wrap(wrap))

    def test_wrap_element(self):
        self.assertEqual(
            self._wrap('foo'),
            [(None, START, u'root'),
             (None, TEXT, u'ROOT'),
             (None, START, u'wrap'),
             (ENTER, START, u'foo'),
             (INSIDE, TEXT, u'FOO'),
             (EXIT, END, u'foo'),
             (None, END, u'wrap'),
             (None, END, u'root')]
            )

    def test_wrap_adjacent_elements(self):
        self.assertEqual(
            _transform(FOOBAR, Transformer('foo|bar').wrap('wrap')),
            [(None, START, u'root'),
             (None, TEXT, u'ROOT'),
             (None, START, u'wrap'),
             (ENTER, START, u'foo'),
             (INSIDE, TEXT, u'FOO'),
             (EXIT, END, u'foo'),
             (None, END, u'wrap'),
             (None, START, u'wrap'),
             (ENTER, START, u'bar'),
             (INSIDE, TEXT, u'BAR'),
             (EXIT, END, u'bar'),
             (None, END, u'wrap'),
             (None, END, u'root')]
            )

    def test_wrap_text(self):
        self.assertEqual(
            self._wrap('foo/text()'),
            [(None, START, u'root'),
             (None, TEXT, u'ROOT'),
             (None, START, u'foo'),
             (None, START, u'wrap'),
             (OUTSIDE, TEXT, u'FOO'),
             (None, END, u'wrap'),
             (None, END, u'foo'),
             (None, END, u'root')]
            )

    def test_wrap_root(self):
        self.assertEqual(
            self._wrap('.'),
            [(None, START, u'wrap'),
             (ENTER, START, u'root'),
             (INSIDE, TEXT, u'ROOT'),
             (INSIDE, START, u'foo'),
             (INSIDE, TEXT, u'FOO'),
             (INSIDE, END, u'foo'),
             (EXIT, END, u'root'),
             (None, END, u'wrap')]
            )

    def test_wrap_text_root(self):
        self.assertEqual(
            _transform('foo', Transformer('.').wrap('wrap')),
            [(None, START, u'wrap'),
             (OUTSIDE, TEXT, u'foo'),
             (None, END, u'wrap')],
            )

    def test_wrap_with_element(self):
        element = Element('a', href='http://localhost')
        self.assertEqual(
            _transform('foo', Transformer('.').wrap(element), with_attrs=True),
            [(None, START, (u'a', {u'href': u'http://localhost'})),
             (OUTSIDE, TEXT, u'foo'),
             (None, END, u'a')]
            )


class FilterTest(unittest.TestCase):
    def _filter(self, select, html=FOOBAR):
        """Returns a list of lists of filtered elements."""
        output = []
        def filtered(stream):
            interval = []
            output.append(interval)
            for event in stream:
                interval.append(event)
                yield event
        _transform(html, Transformer(select).filter(filtered))
        simplified = []
        for sub in output:
            simplified.append(_simplify([(None, event) for event in sub]))
        return simplified

    def test_filter_element(self):
        self.assertEqual(
            self._filter('foo'),
            [[(None, START, u'foo'),
              (None, TEXT, u'FOO'),
              (None, END, u'foo')]]
            )

    def test_filter_adjacent_elements(self):
        self.assertEqual(
            self._filter('foo|bar'),
            [[(None, START, u'foo'),
              (None, TEXT, u'FOO'),
              (None, END, u'foo')],
             [(None, START, u'bar'),
              (None, TEXT, u'BAR'),
              (None, END, u'bar')]]
            )

    def test_filter_text(self):
        self.assertEqual(
            self._filter('*/text()'),
            [[(None, TEXT, u'FOO')],
             [(None, TEXT, u'BAR')]]
            )
    def test_filter_root(self):
        self.assertEqual(
            self._filter('.'),
            [[(None, START, u'root'),
              (None, TEXT, u'ROOT'),
              (None, START, u'foo'),
              (None, TEXT, u'FOO'),
              (None, END, u'foo'),
              (None, START, u'bar'),
              (None, TEXT, u'BAR'),
              (None, END, u'bar'),
              (None, END, u'root')]]
            )

    def test_filter_text_root(self):
        self.assertEqual(
            self._filter('.', 'foo'),
            [[(None, TEXT, u'foo')]])


class MapTest(unittest.TestCase):
    def _map(self, select, kind=None):
        data = []
        def record(d):
            data.append(d)
            return d
        _transform(FOOBAR, Transformer(select).map(record, kind))
        return data

    def test_map_element(self):
        self.assertEqual(
            self._map('foo'),
            [(QName(u'foo'), Attrs([(QName(u'name'), u'foo'),
                                    (QName(u'size'), u'100')])),
             u'FOO',
             QName(u'foo')]
            )

    def test_map_with_text_kind(self):
        self.assertEqual(
            self._map('.', TEXT),
            [u'ROOT', u'FOO', u'BAR']
            )

    def test_map_with_root_and_end_kind(self):
        self.assertEqual(
            self._map('.', END),
            [QName(u'foo'), QName(u'bar'), QName(u'root')]
            )

    def test_map_with_attribute(self):
        self.assertEqual(
            self._map('foo/@name'),
            [(QName(u'foo@*'), Attrs([('name', u'foo')]))]
            )


class SubstituteTest(unittest.TestCase):
    def _substitute(self, select, pattern, replace):
        return _transform(FOOBAR, Transformer(select).substitute(pattern, replace))

    def test_substitute_foo(self):
        self.assertEqual(
            self._substitute('foo', 'FOO|BAR', 'FOOOOO'),
            [(None, START, u'root'),
             (None, TEXT, u'ROOT'),
             (ENTER, START, u'foo'),
             (INSIDE, TEXT, u'FOOOOO'),
             (EXIT, END, u'foo'),
             (None, START, u'bar'),
             (None, TEXT, u'BAR'),
             (None, END, u'bar'),
             (None, END, u'root')]
            )

    def test_substitute_foobar_with_group(self):
        self.assertEqual(
            self._substitute('foo|bar', '(FOO|BAR)', r'(\1)'),
            [(None, START, u'root'),
             (None, TEXT, u'ROOT'),
             (ENTER, START, u'foo'),
             (INSIDE, TEXT, u'(FOO)'),
             (EXIT, END, u'foo'),
             (ENTER, START, u'bar'),
             (INSIDE, TEXT, u'(BAR)'),
             (EXIT, END, u'bar'),
             (None, END, u'root')]
            )


class RenameTest(unittest.TestCase):
    def _rename(self, select):
        return _transform(FOOBAR, Transformer(select).rename('foobar'))

    def test_rename_root(self):
        self.assertEqual(
            self._rename('.'),
            [(ENTER, START, u'foobar'),
             (INSIDE, TEXT, u'ROOT'),
             (INSIDE, START, u'foo'),
             (INSIDE, TEXT, u'FOO'),
             (INSIDE, END, u'foo'),
             (INSIDE, START, u'bar'),
             (INSIDE, TEXT, u'BAR'),
             (INSIDE, END, u'bar'),
             (EXIT, END, u'foobar')]
            )

    def test_rename_element(self):
        self.assertEqual(
            self._rename('foo|bar'),
            [(None, START, u'root'),
             (None, TEXT, u'ROOT'),
             (ENTER, START, u'foobar'),
             (INSIDE, TEXT, u'FOO'),
             (EXIT, END, u'foobar'),
             (ENTER, START, u'foobar'),
             (INSIDE, TEXT, u'BAR'),
             (EXIT, END, u'foobar'),
             (None, END, u'root')]
            )

    def test_rename_text(self):
        self.assertEqual(
            self._rename('foo/text()'),
            [(None, START, u'root'),
             (None, TEXT, u'ROOT'),
             (None, START, u'foo'),
             (OUTSIDE, TEXT, u'FOO'),
             (None, END, u'foo'),
             (None, START, u'bar'),
             (None, TEXT, u'BAR'),
             (None, END, u'bar'),
             (None, END, u'root')]
            )


class ContentTestMixin(object):
    def _apply(self, select, content=None, html=FOOBAR):
        class Injector(object):
            count = 0

            def __iter__(self):
                self.count += 1
                return iter(HTML('CONTENT %i' % self.count))

        if isinstance(html, basestring):
            html = HTML(html)
        if content is None:
            content = Injector()
        elif isinstance(content, basestring):
            content = HTML(content)
        return _transform(html, getattr(Transformer(select), self.operation)
                                (content))


class ReplaceTest(unittest.TestCase, ContentTestMixin):
    operation = 'replace'

    def test_replace_element(self):
        self.assertEqual(
            self._apply('foo'),
            [(None, START, u'root'),
             (None, TEXT, u'ROOT'),
             (None, TEXT, u'CONTENT 1'),
             (None, START, u'bar'),
             (None, TEXT, u'BAR'),
             (None, END, u'bar'),
             (None, END, u'root')]
            )

    def test_replace_text(self):
        self.assertEqual(
            self._apply('text()'),
            [(None, START, u'root'),
             (None, TEXT, u'CONTENT 1'),
             (None, START, u'foo'),
             (None, TEXT, u'FOO'),
             (None, END, u'foo'),
             (None, START, u'bar'),
             (None, TEXT, u'BAR'),
             (None, END, u'bar'),
             (None, END, u'root')]
            )

    def test_replace_context(self):
        self.assertEqual(
            self._apply('.'),
            [(None, TEXT, u'CONTENT 1')],
            )

    def test_replace_text_context(self):
        self.assertEqual(
            self._apply('.', html='foo'),
            [(None, TEXT, u'CONTENT 1')],
            )

    def test_replace_adjacent_elements(self):
        self.assertEqual(
            self._apply('*'),
            [(None, START, u'root'),
             (None, TEXT, u'ROOT'),
             (None, TEXT, u'CONTENT 1'),
             (None, TEXT, u'CONTENT 2'),
             (None, END, u'root')],
            )

    def test_replace_all(self):
        self.assertEqual(
            self._apply('*|text()'),
            [(None, START, u'root'),
             (None, TEXT, u'CONTENT 1'),
             (None, TEXT, u'CONTENT 2'),
             (None, TEXT, u'CONTENT 3'),
             (None, END, u'root')],
            )

    def test_replace_with_callback(self):
        count = [0]
        def content():
            count[0] += 1
            yield '%2i.' % count[0]
        self.assertEqual(
            self._apply('*', content),
            [(None, START, u'root'),
             (None, TEXT, u'ROOT'),
             (None, TEXT, u' 1.'),
             (None, TEXT, u' 2.'),
             (None, END, u'root')]
            )


class BeforeTest(unittest.TestCase, ContentTestMixin):
    operation = 'before'

    def test_before_element(self):
        self.assertEqual(
            self._apply('foo'),
            [(None, START, u'root'),
             (None, TEXT, u'ROOT'),
             (None, TEXT, u'CONTENT 1'),
             (ENTER, START, u'foo'),
             (INSIDE, TEXT, u'FOO'),
             (EXIT, END, u'foo'),
             (None, START, u'bar'),
             (None, TEXT, u'BAR'),
             (None, END, u'bar'),
             (None, END, u'root')]
            )

    def test_before_text(self):
        self.assertEqual(
            self._apply('text()'),
            [(None, START, u'root'),
             (None, TEXT, u'CONTENT 1'),
             (OUTSIDE, TEXT, u'ROOT'),
             (None, START, u'foo'),
             (None, TEXT, u'FOO'),
             (None, END, u'foo'),
             (None, START, u'bar'),
             (None, TEXT, u'BAR'),
             (None, END, u'bar'),
             (None, END, u'root')]
            )

    def test_before_context(self):
        self.assertEqual(
            self._apply('.'),
            [(None, TEXT, u'CONTENT 1'),
             (ENTER, START, u'root'),
             (INSIDE, TEXT, u'ROOT'),
             (INSIDE, START, u'foo'),
             (INSIDE, TEXT, u'FOO'),
             (INSIDE, END, u'foo'),
             (INSIDE, START, u'bar'),
             (INSIDE, TEXT, u'BAR'),
             (INSIDE, END, u'bar'),
             (EXIT, END, u'root')]
            )

    def test_before_text_context(self):
        self.assertEqual(
            self._apply('.', html='foo'),
            [(None, TEXT, u'CONTENT 1'),
             (OUTSIDE, TEXT, u'foo')]
            )

    def test_before_adjacent_elements(self):
        self.assertEqual(
            self._apply('*'),
            [(None, START, u'root'),
             (None, TEXT, u'ROOT'),
             (None, TEXT, u'CONTENT 1'),
             (ENTER, START, u'foo'),
             (INSIDE, TEXT, u'FOO'),
             (EXIT, END, u'foo'),
             (None, TEXT, u'CONTENT 2'),
             (ENTER, START, u'bar'),
             (INSIDE, TEXT, u'BAR'),
             (EXIT, END, u'bar'),
             (None, END, u'root')]

            )

    def test_before_all(self):
        self.assertEqual(
            self._apply('*|text()'),
            [(None, START, u'root'),
             (None, TEXT, u'CONTENT 1'),
             (OUTSIDE, TEXT, u'ROOT'),
             (None, TEXT, u'CONTENT 2'),
             (ENTER, START, u'foo'),
             (INSIDE, TEXT, u'FOO'),
             (EXIT, END, u'foo'),
             (None, TEXT, u'CONTENT 3'),
             (ENTER, START, u'bar'),
             (INSIDE, TEXT, u'BAR'),
             (EXIT, END, u'bar'),
             (None, END, u'root')]
            )

    def test_before_with_callback(self):
        count = [0]
        def content():
            count[0] += 1
            yield '%2i.' % count[0]
        self.assertEqual(
            self._apply('foo/text()', content),
            [(None, 'START', u'root'),
             (None, 'TEXT', u'ROOT'),
             (None, 'START', u'foo'),
             (None, 'TEXT', u' 1.'),
             ('OUTSIDE', 'TEXT', u'FOO'),
             (None, 'END', u'foo'),
             (None, 'START', u'bar'),
             (None, 'TEXT', u'BAR'),
             (None, 'END', u'bar'),
             (None, 'END', u'root')]
            )


class AfterTest(unittest.TestCase, ContentTestMixin):
    operation = 'after'

    def test_after_element(self):
        self.assertEqual(
            self._apply('foo'),
            [(None, START, u'root'),
             (None, TEXT, u'ROOT'),
             (ENTER, START, u'foo'),
             (INSIDE, TEXT, u'FOO'),
             (EXIT, END, u'foo'),
             (None, TEXT, u'CONTENT 1'),
             (None, START, u'bar'),
             (None, TEXT, u'BAR'),
             (None, END, u'bar'),
             (None, END, u'root')]
            )

    def test_after_text(self):
        self.assertEqual(
            self._apply('text()'),
            [(None, START, u'root'),
             (OUTSIDE, TEXT, u'ROOT'),
             (None, TEXT, u'CONTENT 1'),
             (None, START, u'foo'),
             (None, TEXT, u'FOO'),
             (None, END, u'foo'),
             (None, START, u'bar'),
             (None, TEXT, u'BAR'),
             (None, END, u'bar'),
             (None, END, u'root')]
            )

    def test_after_context(self):
        self.assertEqual(
            self._apply('.'),
            [(ENTER, START, u'root'),
             (INSIDE, TEXT, u'ROOT'),
             (INSIDE, START, u'foo'),
             (INSIDE, TEXT, u'FOO'),
             (INSIDE, END, u'foo'),
             (INSIDE, START, u'bar'),
             (INSIDE, TEXT, u'BAR'),
             (INSIDE, END, u'bar'),
             (EXIT, END, u'root'),
             (None, TEXT, u'CONTENT 1')]
            )

    def test_after_text_context(self):
        self.assertEqual(
            self._apply('.', html='foo'),
            [(OUTSIDE, TEXT, u'foo'),
             (None, TEXT, u'CONTENT 1')]
            )

    def test_after_adjacent_elements(self):
        self.assertEqual(
            self._apply('*'),
            [(None, START, u'root'),
             (None, TEXT, u'ROOT'),
             (ENTER, START, u'foo'),
             (INSIDE, TEXT, u'FOO'),
             (EXIT, END, u'foo'),
             (None, TEXT, u'CONTENT 1'),
             (ENTER, START, u'bar'),
             (INSIDE, TEXT, u'BAR'),
             (EXIT, END, u'bar'),
             (None, TEXT, u'CONTENT 2'),
             (None, END, u'root')]

            )

    def test_after_all(self):
        self.assertEqual(
            self._apply('*|text()'),
            [(None, START, u'root'),
             (OUTSIDE, TEXT, u'ROOT'),
             (None, TEXT, u'CONTENT 1'),
             (ENTER, START, u'foo'),
             (INSIDE, TEXT, u'FOO'),
             (EXIT, END, u'foo'),
             (None, TEXT, u'CONTENT 2'),
             (ENTER, START, u'bar'),
             (INSIDE, TEXT, u'BAR'),
             (EXIT, END, u'bar'),
             (None, TEXT, u'CONTENT 3'),
             (None, END, u'root')]
            )

    def test_after_with_callback(self):
        count = [0]
        def content():
            count[0] += 1
            yield '%2i.' % count[0]
        self.assertEqual(
            self._apply('foo/text()', content),
            [(None, 'START', u'root'),
             (None, 'TEXT', u'ROOT'),
             (None, 'START', u'foo'),
             ('OUTSIDE', 'TEXT', u'FOO'),
             (None, 'TEXT', u' 1.'),
             (None, 'END', u'foo'),
             (None, 'START', u'bar'),
             (None, 'TEXT', u'BAR'),
             (None, 'END', u'bar'),
             (None, 'END', u'root')]
            )


class PrependTest(unittest.TestCase, ContentTestMixin):
    operation = 'prepend'

    def test_prepend_element(self):
        self.assertEqual(
            self._apply('foo'),
            [(None, START, u'root'),
             (None, TEXT, u'ROOT'),
             (ENTER, START, u'foo'),
             (None, TEXT, u'CONTENT 1'),
             (INSIDE, TEXT, u'FOO'),
             (EXIT, END, u'foo'),
             (None, START, u'bar'),
             (None, TEXT, u'BAR'),
             (None, END, u'bar'),
             (None, END, u'root')]
            )

    def test_prepend_text(self):
        self.assertEqual(
            self._apply('text()'),
            [(None, START, u'root'),
             (OUTSIDE, TEXT, u'ROOT'),
             (None, START, u'foo'),
             (None, TEXT, u'FOO'),
             (None, END, u'foo'),
             (None, START, u'bar'),
             (None, TEXT, u'BAR'),
             (None, END, u'bar'),
             (None, END, u'root')]
            )

    def test_prepend_context(self):
        self.assertEqual(
            self._apply('.'),
            [(ENTER, START, u'root'),
             (None, TEXT, u'CONTENT 1'),
             (INSIDE, TEXT, u'ROOT'),
             (INSIDE, START, u'foo'),
             (INSIDE, TEXT, u'FOO'),
             (INSIDE, END, u'foo'),
             (INSIDE, START, u'bar'),
             (INSIDE, TEXT, u'BAR'),
             (INSIDE, END, u'bar'),
             (EXIT, END, u'root')],
            )

    def test_prepend_text_context(self):
        self.assertEqual(
            self._apply('.', html='foo'),
            [(OUTSIDE, TEXT, u'foo')]
            )

    def test_prepend_adjacent_elements(self):
        self.assertEqual(
            self._apply('*'),
            [(None, START, u'root'),
             (None, TEXT, u'ROOT'),
             (ENTER, START, u'foo'),
             (None, TEXT, u'CONTENT 1'),
             (INSIDE, TEXT, u'FOO'),
             (EXIT, END, u'foo'),
             (ENTER, START, u'bar'),
             (None, TEXT, u'CONTENT 2'),
             (INSIDE, TEXT, u'BAR'),
             (EXIT, END, u'bar'),
             (None, END, u'root')]

            )

    def test_prepend_all(self):
        self.assertEqual(
            self._apply('*|text()'),
            [(None, START, u'root'),
             (OUTSIDE, TEXT, u'ROOT'),
             (ENTER, START, u'foo'),
             (None, TEXT, u'CONTENT 1'),
             (INSIDE, TEXT, u'FOO'),
             (EXIT, END, u'foo'),
             (ENTER, START, u'bar'),
             (None, TEXT, u'CONTENT 2'),
             (INSIDE, TEXT, u'BAR'),
             (EXIT, END, u'bar'),
             (None, END, u'root')]
            )

    def test_prepend_with_callback(self):
        count = [0]
        def content():
            count[0] += 1
            yield '%2i.' % count[0]
        self.assertEqual(
            self._apply('foo', content),
            [(None, 'START', u'root'),
             (None, 'TEXT', u'ROOT'),
             (ENTER, 'START', u'foo'),
             (None, 'TEXT', u' 1.'),
             (INSIDE, 'TEXT', u'FOO'),
             (EXIT, 'END', u'foo'),
             (None, 'START', u'bar'),
             (None, 'TEXT', u'BAR'),
             (None, 'END', u'bar'),
             (None, 'END', u'root')]
            )


class AppendTest(unittest.TestCase, ContentTestMixin):
    operation = 'append'

    def test_append_element(self):
        self.assertEqual(
            self._apply('foo'),
            [(None, START, u'root'),
             (None, TEXT, u'ROOT'),
             (ENTER, START, u'foo'),
             (INSIDE, TEXT, u'FOO'),
             (None, TEXT, u'CONTENT 1'),
             (EXIT, END, u'foo'),
             (None, START, u'bar'),
             (None, TEXT, u'BAR'),
             (None, END, u'bar'),
             (None, END, u'root')]
            )

    def test_append_text(self):
        self.assertEqual(
            self._apply('text()'),
            [(None, START, u'root'),
             (OUTSIDE, TEXT, u'ROOT'),
             (None, START, u'foo'),
             (None, TEXT, u'FOO'),
             (None, END, u'foo'),
             (None, START, u'bar'),
             (None, TEXT, u'BAR'),
             (None, END, u'bar'),
             (None, END, u'root')]
            )

    def test_append_context(self):
        self.assertEqual(
            self._apply('.'),
            [(ENTER, START, u'root'),
             (INSIDE, TEXT, u'ROOT'),
             (INSIDE, START, u'foo'),
             (INSIDE, TEXT, u'FOO'),
             (INSIDE, END, u'foo'),
             (INSIDE, START, u'bar'),
             (INSIDE, TEXT, u'BAR'),
             (INSIDE, END, u'bar'),
             (None, TEXT, u'CONTENT 1'),
             (EXIT, END, u'root')],
            )

    def test_append_text_context(self):
        self.assertEqual(
            self._apply('.', html='foo'),
            [(OUTSIDE, TEXT, u'foo')]
            )

    def test_append_adjacent_elements(self):
        self.assertEqual(
            self._apply('*'),
            [(None, START, u'root'),
             (None, TEXT, u'ROOT'),
             (ENTER, START, u'foo'),
             (INSIDE, TEXT, u'FOO'),
             (None, TEXT, u'CONTENT 1'),
             (EXIT, END, u'foo'),
             (ENTER, START, u'bar'),
             (INSIDE, TEXT, u'BAR'),
             (None, TEXT, u'CONTENT 2'),
             (EXIT, END, u'bar'),
             (None, END, u'root')]

            )

    def test_append_all(self):
        self.assertEqual(
            self._apply('*|text()'),
            [(None, START, u'root'),
             (OUTSIDE, TEXT, u'ROOT'),
             (ENTER, START, u'foo'),
             (INSIDE, TEXT, u'FOO'),
             (None, TEXT, u'CONTENT 1'),
             (EXIT, END, u'foo'),
             (ENTER, START, u'bar'),
             (INSIDE, TEXT, u'BAR'),
             (None, TEXT, u'CONTENT 2'),
             (EXIT, END, u'bar'),
             (None, END, u'root')]
            )

    def test_append_with_callback(self):
        count = [0]
        def content():
            count[0] += 1
            yield '%2i.' % count[0]
        self.assertEqual(
            self._apply('foo', content),
            [(None, 'START', u'root'),
             (None, 'TEXT', u'ROOT'),
             (ENTER, 'START', u'foo'),
             (INSIDE, 'TEXT', u'FOO'),
             (None, 'TEXT', u' 1.'),
             (EXIT, 'END', u'foo'),
             (None, 'START', u'bar'),
             (None, 'TEXT', u'BAR'),
             (None, 'END', u'bar'),
             (None, 'END', u'root')]
            )



class AttrTest(unittest.TestCase):
    def _attr(self, select, name, value):
        return _transform(FOOBAR, Transformer(select).attr(name, value),
                          with_attrs=True)

    def test_set_existing_attr(self):
        self.assertEqual(
            self._attr('foo', 'name', 'FOO'),
            [(None, START, (u'root', {})),
             (None, TEXT, u'ROOT'),
             (ENTER, START, (u'foo', {u'name': 'FOO', u'size': '100'})),
             (INSIDE, TEXT, u'FOO'),
             (EXIT, END, u'foo'),
             (None, START, (u'bar', {u'name': u'bar'})),
             (None, TEXT, u'BAR'),
             (None, END, u'bar'),
             (None, END, u'root')]
            )

    def test_set_new_attr(self):
        self.assertEqual(
            self._attr('foo', 'title', 'FOO'),
            [(None, START, (u'root', {})),
             (None, TEXT, u'ROOT'),
             (ENTER, START, (u'foo', {u'name': u'foo', u'title': 'FOO', u'size': '100'})),
             (INSIDE, TEXT, u'FOO'),
             (EXIT, END, u'foo'),
             (None, START, (u'bar', {u'name': u'bar'})),
             (None, TEXT, u'BAR'),
             (None, END, u'bar'),
             (None, END, u'root')]
            )

    def test_attr_from_function(self):
        def set(name, event):
            self.assertEqual(name, 'name')
            return event[1][1].get('name').upper()

        self.assertEqual(
            self._attr('foo|bar', 'name', set),
            [(None, START, (u'root', {})),
             (None, TEXT, u'ROOT'),
             (ENTER, START, (u'foo', {u'name': 'FOO', u'size': '100'})),
             (INSIDE, TEXT, u'FOO'),
             (EXIT, END, u'foo'),
             (ENTER, START, (u'bar', {u'name': 'BAR'})),
             (INSIDE, TEXT, u'BAR'),
             (EXIT, END, u'bar'),
             (None, END, u'root')]
            )

    def test_remove_attr(self):
        self.assertEqual(
            self._attr('foo', 'name', None),
            [(None, START, (u'root', {})),
             (None, TEXT, u'ROOT'),
             (ENTER, START, (u'foo', {u'size': '100'})),
             (INSIDE, TEXT, u'FOO'),
             (EXIT, END, u'foo'),
             (None, START, (u'bar', {u'name': u'bar'})),
             (None, TEXT, u'BAR'),
             (None, END, u'bar'),
             (None, END, u'root')]
            )

    def test_remove_attr_with_function(self):
        def set(name, event):
            return None

        self.assertEqual(
            self._attr('foo', 'name', set),
            [(None, START, (u'root', {})),
             (None, TEXT, u'ROOT'),
             (ENTER, START, (u'foo', {u'size': '100'})),
             (INSIDE, TEXT, u'FOO'),
             (EXIT, END, u'foo'),
             (None, START, (u'bar', {u'name': u'bar'})),
             (None, TEXT, u'BAR'),
             (None, END, u'bar'),
             (None, END, u'root')]
            )


class BufferTestMixin(object):
    def _apply(self, select, with_attrs=False):
        buffer = StreamBuffer()
        events = buffer.events

        class Trace(object):
            last = None
            trace = []

            def __call__(self, stream):
                for event in stream:
                    if events and hash(tuple(events)) != self.last:
                        self.last = hash(tuple(events))
                        self.trace.append(list(events))
                    yield event

        trace = Trace()
        output = _transform(FOOBAR, getattr(Transformer(select), self.operation)
                                    (buffer).apply(trace), with_attrs=with_attrs)
        simplified = []
        for interval in trace.trace:
            simplified.append(_simplify([(None, e) for e in interval],
                                         with_attrs=with_attrs))
        return output, simplified


class CopyTest(unittest.TestCase, BufferTestMixin):
    operation = 'copy'

    def test_copy_element(self):
        self.assertEqual(
            self._apply('foo')[1],
            [[(None, START, u'foo'),
              (None, TEXT, u'FOO'),
              (None, END, u'foo')]]
            )

    def test_copy_adjacent_elements(self):
        self.assertEqual(
            self._apply('foo|bar')[1],
            [[(None, START, u'foo'),
              (None, TEXT, u'FOO'),
              (None, END, u'foo')],
             [(None, START, u'bar'),
              (None, TEXT, u'BAR'),
              (None, END, u'bar')]]
            )

    def test_copy_all(self):
        self.assertEqual(
            self._apply('*|text()')[1],
            [[(None, TEXT, u'ROOT')],
             [(None, START, u'foo'),
              (None, TEXT, u'FOO'),
              (None, END, u'foo')],
             [(None, START, u'bar'),
              (None, TEXT, u'BAR'),
              (None, END, u'bar')]]
            )

    def test_copy_text(self):
        self.assertEqual(
            self._apply('*/text()')[1],
            [[(None, TEXT, u'FOO')],
             [(None, TEXT, u'BAR')]]
            )

    def test_copy_context(self):
        self.assertEqual(
            self._apply('.')[1],
            [[(None, START, u'root'),
              (None, TEXT, u'ROOT'),
              (None, START, u'foo'),
              (None, TEXT, u'FOO'),
              (None, END, u'foo'),
              (None, START, u'bar'),
              (None, TEXT, u'BAR'),
              (None, END, u'bar'),
              (None, END, u'root')]]
            )

    def test_copy_attribute(self):
        self.assertEqual(
            self._apply('foo/@name', with_attrs=True)[1],
            [[(None, ATTR, {'name': u'foo'})]]
            )

    def test_copy_attributes(self):
        self.assertEqual(
            self._apply('foo/@*', with_attrs=True)[1],
            [[(None, ATTR, {u'name': u'foo', u'size': u'100'})]]
            )


class CutTest(unittest.TestCase, BufferTestMixin):
    operation = 'cut'

    def test_cut_element(self):
        self.assertEqual(
            self._apply('foo'),
            ([(None, START, u'root'),
              (None, TEXT, u'ROOT'),
              (None, START, u'bar'),
              (None, TEXT, u'BAR'),
              (None, END, u'bar'),
              (None, END, u'root')],
             [[(None, START, u'foo'),
               (None, TEXT, u'FOO'),
               (None, END, u'foo')]])
            )

    def test_cut_adjacent_elements(self):
        self.assertEqual(
            self._apply('foo|bar'),
            ([(None, START, u'root'), 
              (None, TEXT, u'ROOT'),
              (BREAK, BREAK, None),
              (None, END, u'root')],
             [[(None, START, u'foo'),
               (None, TEXT, u'FOO'),
               (None, END, u'foo')],
              [(None, START, u'bar'),
               (None, TEXT, u'BAR'),
               (None, END, u'bar')]])
            )

    def test_cut_all(self):
        self.assertEqual(
            self._apply('*|text()'),
            ([(None, 'START', u'root'),
              ('BREAK', 'BREAK', None),
              ('BREAK', 'BREAK', None),
              (None, 'END', u'root')],
             [[(None, 'TEXT', u'ROOT')],
              [(None, 'START', u'foo'),
               (None, 'TEXT', u'FOO'),
               (None, 'END', u'foo')],
              [(None, 'START', u'bar'),
               (None, 'TEXT', u'BAR'),
               (None, 'END', u'bar')]])
            )

    def test_cut_text(self):
        self.assertEqual(
            self._apply('*/text()'),
            ([(None, 'START', u'root'),
              (None, 'TEXT', u'ROOT'),
              (None, 'START', u'foo'),
              (None, 'END', u'foo'),
              (None, 'START', u'bar'),
              (None, 'END', u'bar'),
              (None, 'END', u'root')],
             [[(None, 'TEXT', u'FOO')],
              [(None, 'TEXT', u'BAR')]])
            )

    def test_cut_context(self):
        self.assertEqual(
            self._apply('.')[1],
            [[(None, 'START', u'root'),
              (None, 'TEXT', u'ROOT'),
              (None, 'START', u'foo'),
              (None, 'TEXT', u'FOO'),
              (None, 'END', u'foo'),
              (None, 'START', u'bar'),
              (None, 'TEXT', u'BAR'),
              (None, 'END', u'bar'),
              (None, 'END', u'root')]]
            )

    def test_cut_attribute(self):
        self.assertEqual(
            self._apply('foo/@name', with_attrs=True),
            ([(None, START, (u'root', {})),
              (None, TEXT, u'ROOT'),
              (None, START, (u'foo', {u'size': u'100'})),
              (None, TEXT, u'FOO'),
              (None, END, u'foo'),
              (None, START, (u'bar', {u'name': u'bar'})),
              (None, TEXT, u'BAR'),
              (None, END, u'bar'),
              (None, END, u'root')],
             [[(None, ATTR, {u'name': u'foo'})]])
            )

    def test_cut_attributes(self):
        self.assertEqual(
            self._apply('foo/@*', with_attrs=True),
            ([(None, START, (u'root', {})),
              (None, TEXT, u'ROOT'),
              (None, START, (u'foo', {})),
              (None, TEXT, u'FOO'),
              (None, END, u'foo'),
              (None, START, (u'bar', {u'name': u'bar'})),
              (None, TEXT, u'BAR'),
              (None, END, u'bar'),
              (None, END, u'root')],
             [[(None, ATTR, {u'name': u'foo', u'size': u'100'})]])
            )

# XXX Test this when the XPath implementation is fixed (#233).
#    def test_cut_attribute_or_attribute(self):
#        self.assertEqual(
#            self._apply('foo/@name | foo/@size', with_attrs=True),
#            ([(None, START, (u'root', {})),
#              (None, TEXT, u'ROOT'),
#              (None, START, (u'foo', {})),
#              (None, TEXT, u'FOO'),
#              (None, END, u'foo'),
#              (None, START, (u'bar', {u'name': u'bar'})),
#              (None, TEXT, u'BAR'),
#              (None, END, u'bar'),
#              (None, END, u'root')],
#             [[(None, ATTR, {u'name': u'foo', u'size': u'100'})]])
#            )




def suite():
    from genshi.input import HTML
    from genshi.core import Markup
    from genshi.builder import tag
    suite = unittest.TestSuite()
    for test in (SelectTest, InvertTest, EndTest,
                 EmptyTest, RemoveTest, UnwrapText, WrapTest, FilterTest,
                 MapTest, SubstituteTest, RenameTest, ReplaceTest, BeforeTest,
                 AfterTest, PrependTest, AppendTest, AttrTest, CopyTest, CutTest):
        suite.addTest(unittest.makeSuite(test, 'test'))
    suite.addTest(doctest.DocTestSuite(
        genshi.filters.transform, optionflags=doctest.NORMALIZE_WHITESPACE,
        extraglobs={'HTML': HTML, 'tag': tag, 'Markup': Markup}))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
