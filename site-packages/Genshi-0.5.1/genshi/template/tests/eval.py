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
import pickle
from StringIO import StringIO
import sys
import unittest

from genshi.core import Markup
from genshi.template.base import Context, _ctxt2dict
from genshi.template.eval import Expression, Suite, Undefined, UndefinedError, \
                                 UNDEFINED


class ExpressionTestCase(unittest.TestCase):

    def test_eq(self):
        expr = Expression('x,y')
        self.assertEqual(expr, Expression('x,y'))
        self.assertNotEqual(expr, Expression('y, x'))

    def test_hash(self):
        expr = Expression('x,y')
        self.assertEqual(hash(expr), hash(Expression('x,y')))
        self.assertNotEqual(hash(expr), hash(Expression('y, x')))

    def test_pickle(self):
        expr = Expression('1 < 2')
        buf = StringIO()
        pickle.dump(expr, buf, 2)
        buf.seek(0)
        unpickled = pickle.load(buf)
        assert unpickled.evaluate({}) is True

    def test_name_lookup(self):
        self.assertEqual('bar', Expression('foo').evaluate({'foo': 'bar'}))
        self.assertEqual(id, Expression('id').evaluate({}))
        self.assertEqual('bar', Expression('id').evaluate({'id': 'bar'}))
        self.assertEqual(None, Expression('id').evaluate({'id': None}))

    def test_builtins(self):
        expr = Expression('Markup')
        self.assertEqual(expr.evaluate({}), Markup)

    def test_str_literal(self):
        self.assertEqual('foo', Expression('"foo"').evaluate({}))
        self.assertEqual('foo', Expression('"""foo"""').evaluate({}))
        self.assertEqual('foo', Expression("'foo'").evaluate({}))
        self.assertEqual('foo', Expression("'''foo'''").evaluate({}))
        self.assertEqual('foo', Expression("u'foo'").evaluate({}))
        self.assertEqual('foo', Expression("r'foo'").evaluate({}))

    def test_str_literal_non_ascii(self):
        expr = Expression(u"u'\xfe'")
        self.assertEqual(u'þ', expr.evaluate({}))
        expr = Expression("u'\xfe'")
        self.assertEqual(u'þ', expr.evaluate({}))
        expr = Expression("'\xc3\xbe'")
        self.assertEqual(u'þ', expr.evaluate({}))

    def test_num_literal(self):
        self.assertEqual(42, Expression("42").evaluate({}))
        self.assertEqual(42L, Expression("42L").evaluate({}))
        self.assertEqual(.42, Expression(".42").evaluate({}))
        self.assertEqual(07, Expression("07").evaluate({}))
        self.assertEqual(0xF2, Expression("0xF2").evaluate({}))
        self.assertEqual(0XF2, Expression("0XF2").evaluate({}))

    def test_dict_literal(self):
        self.assertEqual({}, Expression("{}").evaluate({}))
        self.assertEqual({'key': True},
                         Expression("{'key': value}").evaluate({'value': True}))

    def test_list_literal(self):
        self.assertEqual([], Expression("[]").evaluate({}))
        self.assertEqual([1, 2, 3], Expression("[1, 2, 3]").evaluate({}))
        self.assertEqual([True],
                         Expression("[value]").evaluate({'value': True}))

    def test_tuple_literal(self):
        self.assertEqual((), Expression("()").evaluate({}))
        self.assertEqual((1, 2, 3), Expression("(1, 2, 3)").evaluate({}))
        self.assertEqual((True,),
                         Expression("(value,)").evaluate({'value': True}))

    def test_unaryop_pos(self):
        self.assertEqual(1, Expression("+1").evaluate({}))
        self.assertEqual(1, Expression("+x").evaluate({'x': 1}))

    def test_unaryop_neg(self):
        self.assertEqual(-1, Expression("-1").evaluate({}))
        self.assertEqual(-1, Expression("-x").evaluate({'x': 1}))

    def test_unaryop_not(self):
        self.assertEqual(False, Expression("not True").evaluate({}))
        self.assertEqual(False, Expression("not x").evaluate({'x': True}))

    def test_unaryop_inv(self):
        self.assertEqual(-2, Expression("~1").evaluate({}))
        self.assertEqual(-2, Expression("~x").evaluate({'x': 1}))

    def test_binop_add(self):
        self.assertEqual(3, Expression("2 + 1").evaluate({}))
        self.assertEqual(3, Expression("x + y").evaluate({'x': 2, 'y': 1}))

    def test_binop_sub(self):
        self.assertEqual(1, Expression("2 - 1").evaluate({}))
        self.assertEqual(1, Expression("x - y").evaluate({'x': 1, 'y': 1}))

    def test_binop_sub(self):
        self.assertEqual(1, Expression("2 - 1").evaluate({}))
        self.assertEqual(1, Expression("x - y").evaluate({'x': 2, 'y': 1}))

    def test_binop_mul(self):
        self.assertEqual(4, Expression("2 * 2").evaluate({}))
        self.assertEqual(4, Expression("x * y").evaluate({'x': 2, 'y': 2}))

    def test_binop_pow(self):
        self.assertEqual(4, Expression("2 ** 2").evaluate({}))
        self.assertEqual(4, Expression("x ** y").evaluate({'x': 2, 'y': 2}))

    def test_binop_div(self):
        self.assertEqual(2, Expression("4 / 2").evaluate({}))
        self.assertEqual(2, Expression("x / y").evaluate({'x': 4, 'y': 2}))

    def test_binop_floordiv(self):
        self.assertEqual(1, Expression("3 // 2").evaluate({}))
        self.assertEqual(1, Expression("x // y").evaluate({'x': 3, 'y': 2}))

    def test_binop_mod(self):
        self.assertEqual(1, Expression("3 % 2").evaluate({}))
        self.assertEqual(1, Expression("x % y").evaluate({'x': 3, 'y': 2}))

    def test_binop_and(self):
        self.assertEqual(0, Expression("1 & 0").evaluate({}))
        self.assertEqual(0, Expression("x & y").evaluate({'x': 1, 'y': 0}))

    def test_binop_or(self):
        self.assertEqual(1, Expression("1 | 0").evaluate({}))
        self.assertEqual(1, Expression("x | y").evaluate({'x': 1, 'y': 0}))

    def test_binop_xor(self):
        self.assertEqual(1, Expression("1 ^ 0").evaluate({}))
        self.assertEqual(1, Expression("x ^ y").evaluate({'x': 1, 'y': 0}))

    def test_binop_contains(self):
        self.assertEqual(True, Expression("1 in (1, 2, 3)").evaluate({}))
        self.assertEqual(True, Expression("x in y").evaluate({'x': 1,
                                                              'y': (1, 2, 3)}))

    def test_binop_not_contains(self):
        self.assertEqual(True, Expression("4 not in (1, 2, 3)").evaluate({}))
        self.assertEqual(True, Expression("x not in y").evaluate({'x': 4,
                                                                  'y': (1, 2, 3)}))

    def test_binop_is(self):
        self.assertEqual(True, Expression("1 is 1").evaluate({}))
        self.assertEqual(True, Expression("x is y").evaluate({'x': 1, 'y': 1}))
        self.assertEqual(False, Expression("1 is 2").evaluate({}))
        self.assertEqual(False, Expression("x is y").evaluate({'x': 1, 'y': 2}))

    def test_binop_is_not(self):
        self.assertEqual(True, Expression("1 is not 2").evaluate({}))
        self.assertEqual(True, Expression("x is not y").evaluate({'x': 1,
                                                                  'y': 2}))
        self.assertEqual(False, Expression("1 is not 1").evaluate({}))
        self.assertEqual(False, Expression("x is not y").evaluate({'x': 1,
                                                                   'y': 1}))

    def test_boolop_and(self):
        self.assertEqual(False, Expression("True and False").evaluate({}))
        self.assertEqual(False, Expression("x and y").evaluate({'x': True,
                                                                'y': False}))

    def test_boolop_or(self):
        self.assertEqual(True, Expression("True or False").evaluate({}))
        self.assertEqual(True, Expression("x or y").evaluate({'x': True,
                                                              'y': False}))

    def test_compare_eq(self):
        self.assertEqual(True, Expression("1 == 1").evaluate({}))
        self.assertEqual(True, Expression("x == y").evaluate({'x': 1, 'y': 1}))

    def test_compare_ne(self):
        self.assertEqual(False, Expression("1 != 1").evaluate({}))
        self.assertEqual(False, Expression("x != y").evaluate({'x': 1, 'y': 1}))
        self.assertEqual(False, Expression("1 <> 1").evaluate({}))
        self.assertEqual(False, Expression("x <> y").evaluate({'x': 1, 'y': 1}))

    def test_compare_lt(self):
        self.assertEqual(True, Expression("1 < 2").evaluate({}))
        self.assertEqual(True, Expression("x < y").evaluate({'x': 1, 'y': 2}))

    def test_compare_le(self):
        self.assertEqual(True, Expression("1 <= 1").evaluate({}))
        self.assertEqual(True, Expression("x <= y").evaluate({'x': 1, 'y': 1}))

    def test_compare_gt(self):
        self.assertEqual(True, Expression("2 > 1").evaluate({}))
        self.assertEqual(True, Expression("x > y").evaluate({'x': 2, 'y': 1}))

    def test_compare_ge(self):
        self.assertEqual(True, Expression("1 >= 1").evaluate({}))
        self.assertEqual(True, Expression("x >= y").evaluate({'x': 1, 'y': 1}))

    def test_compare_multi(self):
        self.assertEqual(True, Expression("1 != 3 == 3").evaluate({}))
        self.assertEqual(True, Expression("x != y == y").evaluate({'x': 1,
                                                                   'y': 3}))

    def test_call_function(self):
        self.assertEqual(42, Expression("foo()").evaluate({'foo': lambda: 42}))
        data = {'foo': 'bar'}
        self.assertEqual('BAR', Expression("foo.upper()").evaluate(data))
        data = {'foo': {'bar': range(42)}}
        self.assertEqual(42, Expression("len(foo.bar)").evaluate(data))

    def test_call_keywords(self):
        self.assertEqual(42, Expression("foo(x=bar)").evaluate({'foo': lambda x: x,
                                                                'bar': 42}))

    def test_call_star_args(self):
        self.assertEqual(42, Expression("foo(*bar)").evaluate({'foo': lambda x: x,
                                                               'bar': [42]}))

    def test_call_dstar_args(self):
        def foo(x):
            return x
        expr = Expression("foo(**bar)")
        self.assertEqual(42, expr.evaluate({'foo': foo, 'bar': {"x": 42}}))

    def test_lambda(self):
        # Define a custom `sorted` function cause the builtin isn't available
        # on Python 2.3
        def sorted(items, compfunc):
            items.sort(compfunc)
            return items
        data = {'items': [{'name': 'b', 'value': 0}, {'name': 'a', 'value': 1}],
                'sorted': sorted}
        expr = Expression("sorted(items, lambda a, b: cmp(a.name, b.name))")
        self.assertEqual([{'name': 'a', 'value': 1}, {'name': 'b', 'value': 0}],
                         expr.evaluate(data))

    def test_list_comprehension(self):
        expr = Expression("[n for n in numbers if n < 2]")
        self.assertEqual([0, 1], expr.evaluate({'numbers': range(5)}))

        expr = Expression("[(i, n + 1) for i, n in enumerate(numbers)]")
        self.assertEqual([(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)],
                         expr.evaluate({'numbers': range(5)}))

        expr = Expression("[offset + n for n in numbers]")
        self.assertEqual([2, 3, 4, 5, 6],
                         expr.evaluate({'numbers': range(5), 'offset': 2}))

    def test_list_comprehension_with_getattr(self):
        items = [{'name': 'a', 'value': 1}, {'name': 'b', 'value': 2}]
        expr = Expression("[i.name for i in items if i.value > 1]")
        self.assertEqual(['b'], expr.evaluate({'items': items}))

    def test_list_comprehension_with_getitem(self):
        items = [{'name': 'a', 'value': 1}, {'name': 'b', 'value': 2}]
        expr = Expression("[i['name'] for i in items if i['value'] > 1]")
        self.assertEqual(['b'], expr.evaluate({'items': items}))

    if sys.version_info >= (2, 4):
        # Generator expressions only supported in Python 2.4 and up

        def test_generator_expression(self):
            expr = Expression("list(n for n in numbers if n < 2)")
            self.assertEqual([0, 1], expr.evaluate({'numbers': range(5)}))

            expr = Expression("list((i, n + 1) for i, n in enumerate(numbers))")
            self.assertEqual([(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)],
                             expr.evaluate({'numbers': range(5)}))

            expr = Expression("list(offset + n for n in numbers)")
            self.assertEqual([2, 3, 4, 5, 6],
                             expr.evaluate({'numbers': range(5), 'offset': 2}))

        def test_generator_expression_with_getattr(self):
            items = [{'name': 'a', 'value': 1}, {'name': 'b', 'value': 2}]
            expr = Expression("list(i.name for i in items if i.value > 1)")
            self.assertEqual(['b'], expr.evaluate({'items': items}))

        def test_generator_expression_with_getitem(self):
            items = [{'name': 'a', 'value': 1}, {'name': 'b', 'value': 2}]
            expr = Expression("list(i['name'] for i in items if i['value'] > 1)")
            self.assertEqual(['b'], expr.evaluate({'items': items}))

    if sys.version_info >= (2, 5):
        def test_conditional_expression(self):
            expr = Expression("'T' if foo else 'F'")
            self.assertEqual('T', expr.evaluate({'foo': True}))
            self.assertEqual('F', expr.evaluate({'foo': False}))

    def test_slice(self):
        expr = Expression("numbers[0:2]")
        self.assertEqual([0, 1], expr.evaluate({'numbers': range(5)}))

    def test_slice_with_vars(self):
        expr = Expression("numbers[start:end]")
        self.assertEqual([0, 1], expr.evaluate({'numbers': range(5), 'start': 0,
                                                'end': 2}))

    def test_slice_copy(self):
        expr = Expression("numbers[:]")
        self.assertEqual([0, 1, 2, 3, 4], expr.evaluate({'numbers': range(5)}))

    def test_slice_stride(self):
        expr = Expression("numbers[::stride]")
        self.assertEqual([0, 2, 4], expr.evaluate({'numbers': range(5),
                                                   'stride': 2}))

    def test_slice_negative_start(self):
        expr = Expression("numbers[-1:]")
        self.assertEqual([4], expr.evaluate({'numbers': range(5)}))

    def test_slice_negative_end(self):
        expr = Expression("numbers[:-1]")
        self.assertEqual([0, 1, 2, 3], expr.evaluate({'numbers': range(5)}))

    def test_access_undefined(self):
        expr = Expression("nothing", filename='index.html', lineno=50,
                          lookup='lenient')
        retval = expr.evaluate({})
        assert isinstance(retval, Undefined)
        self.assertEqual('nothing', retval._name)
        assert retval._owner is UNDEFINED

    def test_getattr_undefined(self):
        class Something(object):
            def __repr__(self):
                return '<Something>'
        something = Something()
        expr = Expression('something.nil', filename='index.html', lineno=50,
                          lookup='lenient')
        retval = expr.evaluate({'something': something})
        assert isinstance(retval, Undefined)
        self.assertEqual('nil', retval._name)
        assert retval._owner is something

    def test_getattr_exception(self):
        class Something(object):
            def prop_a(self):
                raise NotImplementedError
            prop_a = property(prop_a)
            def prop_b(self):
                raise AttributeError
            prop_b = property(prop_b)
        self.assertRaises(NotImplementedError,
                          Expression('s.prop_a').evaluate, {'s': Something()})
        self.assertRaises(AttributeError,
                          Expression('s.prop_b').evaluate, {'s': Something()})

    def test_getitem_undefined_string(self):
        class Something(object):
            def __repr__(self):
                return '<Something>'
        something = Something()
        expr = Expression('something["nil"]', filename='index.html', lineno=50,
                          lookup='lenient')
        retval = expr.evaluate({'something': something})
        assert isinstance(retval, Undefined)
        self.assertEqual('nil', retval._name)
        assert retval._owner is something

    def test_getitem_exception(self):
        class Something(object):
            def __getitem__(self, key):
                raise NotImplementedError
        self.assertRaises(NotImplementedError,
                          Expression('s["foo"]').evaluate, {'s': Something()})

    def test_error_access_undefined(self):
        expr = Expression("nothing", filename='index.html', lineno=50,
                          lookup='strict')
        try:
            expr.evaluate({})
            self.fail('Expected UndefinedError')
        except UndefinedError, e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            frame = exc_traceback.tb_next
            frames = []
            while frame.tb_next:
                frame = frame.tb_next
                frames.append(frame)
            self.assertEqual('"nothing" not defined', str(e))
            self.assertEqual("<Expression 'nothing'>",
                             frames[-3].tb_frame.f_code.co_name)
            self.assertEqual('index.html',
                             frames[-3].tb_frame.f_code.co_filename)
            self.assertEqual(50, frames[-3].tb_lineno)

    def test_error_getattr_undefined(self):
        class Something(object):
            def __repr__(self):
                return '<Something>'
        expr = Expression('something.nil', filename='index.html', lineno=50,
                          lookup='strict')
        try:
            expr.evaluate({'something': Something()})
            self.fail('Expected UndefinedError')
        except UndefinedError, e:
            self.assertEqual('<Something> has no member named "nil"', str(e))
            exc_type, exc_value, exc_traceback = sys.exc_info()
            search_string = "<Expression 'something.nil'>"
            frame = exc_traceback.tb_next
            while frame.tb_next:
                frame = frame.tb_next
                code = frame.tb_frame.f_code
                if code.co_name == search_string:
                    break
            else:
                self.fail("never found the frame I was looking for")
            self.assertEqual('index.html', code.co_filename)
            self.assertEqual(50, frame.tb_lineno)

    def test_error_getitem_undefined_string(self):
        class Something(object):
            def __repr__(self):
                return '<Something>'
        expr = Expression('something["nil"]', filename='index.html', lineno=50,
                          lookup='strict')
        try:
            expr.evaluate({'something': Something()})
            self.fail('Expected UndefinedError')
        except UndefinedError, e:
            self.assertEqual('<Something> has no member named "nil"', str(e))
            exc_type, exc_value, exc_traceback = sys.exc_info()
            search_string = '''<Expression 'something["nil"]'>'''
            frame = exc_traceback.tb_next
            while frame.tb_next:
                frame = frame.tb_next
                code = frame.tb_frame.f_code
                if code.co_name == search_string:
                    break
            else:
                self.fail("never found the frame I was looking for")
            self.assertEqual('index.html', code.co_filename)
            self.assertEqual(50, frame.tb_lineno)


class SuiteTestCase(unittest.TestCase):

    def test_pickle(self):
        suite = Suite('foo = 42')
        buf = StringIO()
        pickle.dump(suite, buf, 2)
        buf.seek(0)
        unpickled = pickle.load(buf)
        data = {}
        unpickled.execute(data)
        self.assertEqual(42, data['foo'])

    def test_internal_shadowing(self):
        # The context itself is stored in the global execution scope of a suite
        # It used to get stored under the name 'data', which meant the
        # following test would fail, as the user defined 'data' variable
        # shadowed the Genshi one. We now use the name '__data__' to avoid
        # conflicts
        suite = Suite("""data = []
bar = foo
""")
        data = {'foo': 42}
        suite.execute(data)
        self.assertEqual(42, data['bar'])

    def test_assign(self):
        suite = Suite("foo = 42")
        data = {}
        suite.execute(data)
        self.assertEqual(42, data['foo'])

    def test_def(self):
        suite = Suite("def donothing(): pass")
        data = {}
        suite.execute(data)
        assert 'donothing' in data
        self.assertEqual(None, data['donothing']())

    def test_def_with_multiple_statements(self):
        suite = Suite("""
def donothing():
    if True:
        return foo
""")
        data = {'foo': 'bar'}
        suite.execute(data)
        assert 'donothing' in data
        self.assertEqual('bar', data['donothing']())

    def test_def_using_nonlocal(self):
        suite = Suite("""
values = []
def add(value):
    if value not in values:
        values.append(value)
add('foo')
add('bar')
""")
        data = {}
        suite.execute(data)
        self.assertEqual(['foo', 'bar'], data['values'])

    def test_def_nested(self):
        suite = Suite("""
def doit():
    values = []
    def add(value):
        if value not in values:
            values.append(value)
    add('foo')
    add('bar')
    return values
x = doit()
""")
        data = {}
        suite.execute(data)
        self.assertEqual(['foo', 'bar'], data['x'])

    def test_delete(self):
        suite = Suite("""foo = 42
del foo
""")
        data = {}
        suite.execute(data)
        assert 'foo' not in data

    def test_class(self):
        suite = Suite("class plain(object): pass")
        data = {}
        suite.execute(data)
        assert 'plain' in data

    def test_class_in_def(self):
        suite = Suite("""
def create():
    class Foobar(object):
        def __str__(self):
            return 'foobar'
    return Foobar()
x = create()
""")
        data = {}
        suite.execute(data)
        self.assertEqual('foobar', str(data['x']))

    def test_class_with_methods(self):
        suite = Suite("""class plain(object):
    def donothing():
        pass
""")
        data = {}
        suite.execute(data)
        assert 'plain' in data

    def test_import(self):
        suite = Suite("from itertools import ifilter")
        data = {}
        suite.execute(data)
        assert 'ifilter' in data

    def test_import_star(self):
        suite = Suite("from itertools import *")
        data = Context()
        suite.execute(_ctxt2dict(data))
        assert 'ifilter' in data

    def test_for(self):
        suite = Suite("""x = []
for i in range(3):
    x.append(i**2)
""")
        data = {}
        suite.execute(data)
        self.assertEqual([0, 1, 4], data['x'])

    def test_if(self):
        suite = Suite("""if foo == 42:
    x = True
""")
        data = {'foo': 42}
        suite.execute(data)
        self.assertEqual(True, data['x'])

    def test_raise(self):
        suite = Suite("""raise NotImplementedError""")
        self.assertRaises(NotImplementedError, suite.execute, {})

    def test_try_except(self):
        suite = Suite("""try:
    import somemod
except ImportError:
    somemod = None
else:
    somemod.dosth()""")
        data = {}
        suite.execute(data)
        self.assertEqual(None, data['somemod'])

    def test_finally(self):
        suite = Suite("""try:
    x = 2
finally:
    x = None
""")
        data = {}
        suite.execute(data)
        self.assertEqual(None, data['x'])

    def test_while_break(self):
        suite = Suite("""x = 0
while x < 5:
    x += step
    if x == 4:
        break
""")
        data = {'step': 2}
        suite.execute(data)
        self.assertEqual(4, data['x'])

    def test_augmented_attribute_assignment(self):
        suite = Suite("d['k'] += 42")
        d = {"k": 1}
        suite.execute({"d": d})
        self.assertEqual(43, d["k"])

    def test_local_augmented_assign(self):
        Suite("x = 1; x += 42; assert x == 43").execute({})

    def test_augmented_assign_in_def(self):
        d = {}
        Suite("""def foo():
    i = 1
    i += 1
    return i
x = foo()""").execute(d)
        self.assertEqual(2, d['x'])

    def test_augmented_assign_in_loop_in_def(self):
        d = {}
        Suite("""def foo():
    i = 0
    for n in range(5):
        i += n
    return i
x = foo()""").execute(d)
        self.assertEqual(10, d['x'])

    def test_assign_in_list(self):
        suite = Suite("[d['k']] = 'foo',; assert d['k'] == 'foo'")
        d = {"k": "bar"}
        suite.execute({"d": d})
        self.assertEqual("foo", d["k"])

    def test_exec(self):
        suite = Suite("x = 1; exec d['k']; assert x == 42, x")
        suite.execute({"d": {"k": "x = 42"}})

    def test_return(self):
        suite = Suite("""
def f():
    return v

assert f() == 42
""")
        suite.execute({"v": 42})

    def test_assign_to_dict_item(self):
        suite = Suite("d['k'] = 'foo'")
        data = {'d': {}}
        suite.execute(data)
        self.assertEqual('foo', data['d']['k'])

    def test_assign_to_attribute(self):
        class Something(object): pass
        something = Something()
        suite = Suite("obj.attr = 'foo'")
        data = {"obj": something}
        suite.execute(data)
        self.assertEqual('foo', something.attr)

    def test_delattr(self):
        class Something(object):
            def __init__(self):
                self.attr = 'foo'
        obj = Something()
        Suite("del obj.attr").execute({'obj': obj})
        self.failIf(hasattr(obj, 'attr'))

    def test_delitem(self):
        d = {'k': 'foo'}
        Suite("del d['k']").execute({'d': d})
        self.failIf('k' in d, `d`)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite(Expression.__module__))
    suite.addTest(unittest.makeSuite(ExpressionTestCase, 'test'))
    suite.addTest(unittest.makeSuite(SuiteTestCase, 'test'))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
