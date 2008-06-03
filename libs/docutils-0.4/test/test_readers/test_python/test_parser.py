#! /usr/bin/env python

# Author: David Goodger
# Contact: goodger@users.sourceforge.net
# Revision: $Revision: 3085 $
# Date: $Date: 2005-03-22 21:38:43 +0100 (Tue, 22 Mar 2005) $
# Copyright: This module has been placed in the public domain.

"""
Tests for docutils/readers/python/moduleparser.py.
"""

from __init__ import DocutilsTestSupport


def suite():
    s = DocutilsTestSupport.PythonModuleParserTestSuite()
    s.generateTests(totest)
    return s

totest = {}

totest['module'] = [
['''\
''',
'''\
<module_section filename="test data">
'''],
['''\
"""docstring"""
''',
'''\
<module_section filename="test data">
    <docstring>
        docstring
'''],
['''\
u"""Unicode docstring"""
''',
'''\
<module_section filename="test data">
    <docstring>
        Unicode docstring
'''],
['''\
"""docstring"""
"""additional docstring"""
''',
'''\
<module_section filename="test data">
    <docstring>
        docstring
    <docstring lineno="2">
        additional docstring
'''],
['''\
"""docstring"""
# comment
"""additional docstring"""
''',
'''\
<module_section filename="test data">
    <docstring>
        docstring
    <docstring lineno="3">
        additional docstring
'''],
['''\
"""docstring"""
1
"""not an additional docstring"""
''',
'''\
<module_section filename="test data">
    <docstring>
        docstring
'''],
]

totest['import'] = [
['''\
import module
''',
'''\
<module_section filename="test data">
    <import_group lineno="1">
        <import_name>
            module
'''],
['''\
import module as local
''',
'''\
<module_section filename="test data">
    <import_group lineno="1">
        <import_name>
            module
            <import_alias>
                local
'''],
['''\
import module.name
''',
'''\
<module_section filename="test data">
    <import_group lineno="1">
        <import_name>
            module.name
'''],
['''\
import module.name as local
''',
'''\
<module_section filename="test data">
    <import_group lineno="1">
        <import_name>
            module.name
            <import_alias>
                local
'''],
['''\
import module
"""not documentable"""
''',
'''\
<module_section filename="test data">
    <import_group lineno="1">
        <import_name>
            module
'''],
]

totest['from'] = [
['''\
from module import name
''',
'''\
<module_section filename="test data">
    <import_group lineno="1">
        <import_from>
            module
        <import_name>
            name
'''],
['''\
from module import name as local
''',
'''\
<module_section filename="test data">
    <import_group lineno="1">
        <import_from>
            module
        <import_name>
            name
            <import_alias>
                local
'''],
['''\
from module import name1, name2 as local2
''',
'''\
<module_section filename="test data">
    <import_group lineno="1">
        <import_from>
            module
        <import_name>
            name1
        <import_name>
            name2
            <import_alias>
                local2
'''],
['''\
from module.sub import name
''',
'''\
<module_section filename="test data">
    <import_group lineno="1">
        <import_from>
            module.sub
        <import_name>
            name
'''],
['''\
from module.sub import name as local
''',
'''\
<module_section filename="test data">
    <import_group lineno="1">
        <import_from>
            module.sub
        <import_name>
            name
            <import_alias>
                local
'''],
['''\
from module import *
''',
'''\
<module_section filename="test data">
    <import_group lineno="1">
        <import_from>
            module
        <import_name>
            *
'''],
['''\
from __future__ import division
''',
'''\
<module_section filename="test data">
    <import_group lineno="1">
        <import_from>
            __future__
        <import_name>
            division
'''],
]

totest['assign'] = [
['''\
a = 1
''',
'''\
<module_section filename="test data">
    <attribute lineno="1">
        <object_name>
            a
        <expression_value>
            1
'''],
['''a = 1''',
'''\
<module_section filename="test data">
    <attribute lineno="1">
        <object_name>
            a
        <expression_value>
            1
'''],
['''\
a = 1
"""a docstring"""
''', #"
'''\
<module_section filename="test data">
    <attribute lineno="1">
        <object_name>
            a
        <expression_value>
            1
        <docstring lineno="2">
            a docstring
'''],
['''\
a = 1
"""a docstring"""
"""additional docstring"""
''', #"
'''\
<module_section filename="test data">
    <attribute lineno="1">
        <object_name>
            a
        <expression_value>
            1
        <docstring lineno="2">
            a docstring
        <docstring lineno="3">
            additional docstring
'''], #'
['''\
a = 1 + 2 * 3 / 4 ** 5
''',
'''\
<module_section filename="test data">
    <attribute lineno="1">
        <object_name>
            a
        <expression_value>
            1 + 2 * 3 / 4 ** 5
'''],
['''\
a = 1 \\
    + 2
''',
'''\
<module_section filename="test data">
    <attribute lineno="1">
        <object_name>
            a
        <expression_value>
            1 + 2
'''],
['''\
a = not 1 and 2 or 3
''',
'''\
<module_section filename="test data">
    <attribute lineno="1">
        <object_name>
            a
        <expression_value>
            not 1 and 2 or 3
'''],
['''\
a = ~ 1 & 2 | 3 ^ 4
''',
'''\
<module_section filename="test data">
    <attribute lineno="1">
        <object_name>
            a
        <expression_value>
            ~ 1 & 2 | 3 ^ 4
'''],
['''\
a = `1 & 2`
''',
'''\
<module_section filename="test data">
    <attribute lineno="1">
        <object_name>
            a
        <expression_value>
            `1 & 2`
'''],
['''\
very_long_name = \\
    x
''',
'''\
<module_section filename="test data">
    <attribute lineno="1">
        <object_name>
            very_long_name
        <expression_value>
            x
'''],
['''\
very_long_name \\
    = x
''',
'''\
<module_section filename="test data">
    <attribute lineno="1">
        <object_name>
            very_long_name
        <expression_value>
            x
'''],
['''\
very_long_name = \\
    another_long_name = \\
    x
''',
'''\
<module_section filename="test data">
    <attribute lineno="1">
        <object_name>
            very_long_name
        <expression_value>
            x
    <attribute lineno="2">
        <object_name>
            another_long_name
        <expression_value>
            x
'''],
['''\
a = (1
     + 2)
b = a.b[1 +
        fn(x, y,
           z, {'key': (1 + 2
                       + 3)})][4]
c = """first line
second line
    third"""
''',
'''\
<module_section filename="test data">
    <attribute lineno="1">
        <object_name>
            a
        <expression_value>
            (1 + 2)
    <attribute lineno="3">
        <object_name>
            b
        <expression_value>
            a.b[1 + fn(x, y, z, {'key': (1 + 2 + 3)})][4]
    <attribute lineno="7">
        <object_name>
            c
        <expression_value>
            """first line
            second line
                third"""
'''],
['''\
a, b, c = range(3)
(d, e,
 f) = a, b, c
g, h, i = j = a, b, c
k.a, k.b.c, k.d.e.f = a, b, c
''',
'''\
<module_section filename="test data">
    <attribute_tuple lineno="1">
        <attribute lineno="1">
            <object_name>
                a
        <attribute lineno="1">
            <object_name>
                b
        <attribute lineno="1">
            <object_name>
                c
        <expression_value>
            range(3)
    <attribute_tuple lineno="2">
        <attribute lineno="2">
            <object_name>
                d
        <attribute lineno="2">
            <object_name>
                e
        <attribute lineno="3">
            <object_name>
                f
        <expression_value>
            a, b, c
    <attribute_tuple lineno="4">
        <attribute lineno="4">
            <object_name>
                g
        <attribute lineno="4">
            <object_name>
                h
        <attribute lineno="4">
            <object_name>
                i
        <expression_value>
            a, b, c
    <attribute lineno="4">
        <object_name>
            j
        <expression_value>
            a, b, c
    <attribute_tuple lineno="5">
        <attribute lineno="5">
            <object_name>
                k.a
        <attribute lineno="5">
            <object_name>
                k.b.c
        <attribute lineno="5">
            <object_name>
                k.d.e.f
        <expression_value>
            a, b, c
'''],
['''\
a = 1 ; b = 2
print ; c = 3
''',
'''\
<module_section filename="test data">
    <attribute lineno="1">
        <object_name>
            a
        <expression_value>
            1
    <attribute lineno="1">
        <object_name>
            b
        <expression_value>
            2
    <attribute lineno="2">
        <object_name>
            c
        <expression_value>
            3
'''],
['''\
a.b = 1
"""This assignment is noted but ignored unless ``a`` is a function."""
''',
'''\
<module_section filename="test data">
    <attribute lineno="1">
        <object_name>
            a.b
        <expression_value>
            1
        <docstring lineno="2">
            This assignment is noted but ignored unless ``a`` is a function.
'''],
['''\
a[b] = 1
"""Subscript assignments are ignored."""
''',
'''\
<module_section filename="test data">
'''],
['''\
a = foo(b=1)
''',
'''\
<module_section filename="test data">
    <attribute lineno="1">
        <object_name>
            a
        <expression_value>
            foo(b=1)
'''],
# ['''\
# a = 1
# 
# """Because of the blank above, this is a module docstring."""
# ''',
# '''\
# <module_section filename="test data">
#     <attribute lineno="1">
#         <object_name>
#             a
#         <expression_value>
#             1
#     <docstring lineno="3">
#         Because of the blank above, this is a module docstring.
# '''],
]

totest['def'] = [
['''\
def f():
    """Function f docstring"""
    """Additional docstring"""
    local = 1
    """Not a docstring, since ``local`` is local."""
''', # "
'''\
<module_section filename="test data">
    <function_section lineno="1">
        <object_name>
            f
        <docstring lineno="1">
            Function f docstring
        <docstring lineno="3">
            Additional docstring
'''], # '
['''\
def f(a, b):
    local = 1
''',
'''\
<module_section filename="test data">
    <function_section lineno="1">
        <object_name>
            f
        <parameter_list>
            <parameter>
                <object_name>
                    a
            <parameter>
                <object_name>
                    b
'''],
['''\
def f(a=None, b=1):
    local = 1
''',
'''\
<module_section filename="test data">
    <function_section lineno="1">
        <object_name>
            f
        <parameter_list>
            <parameter>
                <object_name>
                    a
                <parameter_default>
                    None
            <parameter>
                <object_name>
                    b
                <parameter_default>
                    1
'''],
['''\
def f(a, (b, c, d)=range(3),
      e=None):
    local = 1
''',
'''\
<module_section filename="test data">
    <function_section lineno="1">
        <object_name>
            f
        <parameter_list>
            <parameter>
                <object_name>
                    a
            <parameter_tuple>
                <parameter>
                    <object_name>
                        b
                <parameter>
                    <object_name>
                        c
                <parameter>
                    <object_name>
                        d
                <parameter_default>
                    range(3)
            <parameter>
                <object_name>
                    e
                <parameter_default>
                    None
'''],
['''\
def f(*args):
    local = 1
''',
'''\
<module_section filename="test data">
    <function_section lineno="1">
        <object_name>
            f
        <parameter_list>
            <parameter excess_positional="1">
                <object_name>
                    args
'''],
['''\
def f(**kwargs):
    local = 1
''',
'''\
<module_section filename="test data">
    <function_section lineno="1">
        <object_name>
            f
        <parameter_list>
            <parameter excess_keyword="1">
                <object_name>
                    kwargs
'''],
['''\
def f(a, b=None, *args, **kwargs):
    local = 1
''',
'''\
<module_section filename="test data">
    <function_section lineno="1">
        <object_name>
            f
        <parameter_list>
            <parameter>
                <object_name>
                    a
            <parameter>
                <object_name>
                    b
                <parameter_default>
                    None
            <parameter excess_positional="1">
                <object_name>
                    args
            <parameter excess_keyword="1">
                <object_name>
                    kwargs
'''],
['''\
def f():
    pass
f.attrib = 1
"""f.attrib docstring"""
''', # "
# @@@ When should the attribute move inside the Function?
'''\
<module_section filename="test data">
    <function_section lineno="1">
        <object_name>
            f
    <attribute lineno="3">
        <object_name>
            f.attrib
        <expression_value>
            1
        <docstring lineno="4">
            f.attrib docstring
'''], 
['''\
def f():
    def g():
        pass
    """Not a docstring"""
    local = 1
''',
'''\
<module_section filename="test data">
    <function_section lineno="1">
        <object_name>
            f
'''],
]

totest['class'] = [
['''\
class C:
    """class C docstring"""
''',
'''\
<module_section filename="test data">
    <class_section lineno="1">
        <object_name>
            C
        <docstring lineno="1">
            class C docstring
'''],
['''\
class C(Super):
    pass

class D(SuperD, package.module.SuperD):
    pass
''',
'''\
<module_section filename="test data">
    <class_section lineno="1">
        <object_name>
            C
        <class_base>
            <object_name>
                Super
    <class_section lineno="4">
        <object_name>
            D
        <class_base>
            <object_name>
                SuperD
        <class_base>
            <object_name>
                package.module.SuperD
'''],
['''\
class C:
    class D:
        pass
    """Not a docstring"""
''',
'''\
<module_section filename="test data">
    <class_section lineno="1">
        <object_name>
            C
'''],
['''\
class C:
    def f(self):
        self.local = 1
        local = 1
''',
'''\
<module_section filename="test data">
    <class_section lineno="1">
        <object_name>
            C
        <method_section lineno="2">
            <object_name>
                f
            <parameter_list>
                <parameter>
                    <object_name>
                        self
'''],
['''\
class C:
    def __init__(self):
        self.local = 1
        local = 1
''',
'''\
<module_section filename="test data">
    <class_section lineno="1">
        <object_name>
            C
        <method_section lineno="2">
            <object_name>
                __init__
            <parameter_list>
                <parameter>
                    <object_name>
                        self
            <attribute lineno="3">
                <object_name>
                    self.local
                <expression_value>
                    1
            <attribute lineno="4">
                <object_name>
                    local
                <expression_value>
                    1
'''],
['''\
class C:
    def __init__(self):
        local = foo(a=1)
''',
'''\
<module_section filename="test data">
    <class_section lineno="1">
        <object_name>
            C
        <method_section lineno="2">
            <object_name>
                __init__
            <parameter_list>
                <parameter>
                    <object_name>
                        self
            <attribute lineno="3">
                <object_name>
                    local
                <expression_value>
                    foo(a=1)
'''],
]

totest['ignore'] = [
['''\
1 + 2
''',
'''\
<module_section filename="test data">
'''],
['''\
del a
''',
'''\
<module_section filename="test data">
'''],
]

totest['comments'] = [
# ['''\
# # Comment
# ''',
# '''\
# <module_section filename="test data">
#     <Comment lineno="1">
#         # Comment
# '''],
]

# @@@ we don't parse comments yet
totest['everything'] = [
['''\
# comment

"""Docstring"""

"""Additional docstring"""

__docformat__ = 'reStructuredText'

a = 1
"""Attribute docstring"""

class C(Super):

    """C docstring"""

    class_attribute = 1
    """class_attribute docstring"""

    def __init__(self, text=None):
        """__init__ docstring"""

        self.instance_attribute = (text * 7
                                   + ' whaddyaknow')
        """instance_attribute docstring"""


def f(x,                            # parameter x
      y=a*5,                        # parameter y
      *args):                       # parameter args
    """f docstring"""
    return [x + item for item in args]

f.function_attribute = 1
"""f.function_attribute docstring"""
''',
'''\
<module_section filename="test data">
    <docstring>
        Docstring
    <docstring lineno="5">
        Additional docstring
    <attribute lineno="7">
        <object_name>
            __docformat__
        <expression_value>
            'reStructuredText'
    <attribute lineno="9">
        <object_name>
            a
        <expression_value>
            1
        <docstring lineno="10">
            Attribute docstring
    <class_section lineno="12">
        <object_name>
            C
        <class_base>
            <object_name>
                Super
        <docstring lineno="12">
            C docstring
        <attribute lineno="16">
            <object_name>
                class_attribute
            <expression_value>
                1
            <docstring lineno="17">
                class_attribute docstring
        <method_section lineno="19">
            <object_name>
                __init__
            <docstring lineno="19">
                __init__ docstring
            <parameter_list>
                <parameter>
                    <object_name>
                        self
                <parameter>
                    <object_name>
                        text
                    <parameter_default>
                        None
            <attribute lineno="22">
                <object_name>
                    self.instance_attribute
                <expression_value>
                    (text * 7 + ' whaddyaknow')
                <docstring lineno="24">
                    instance_attribute docstring
    <function_section lineno="27">
        <object_name>
            f
        <docstring lineno="27">
            f docstring
        <parameter_list>
            <parameter>
                <object_name>
                    x
            <parameter>
                <object_name>
                    y
                <parameter_default>
                    a * 5
            <parameter excess_positional="1">
                <object_name>
                    args
    <attribute lineno="33">
        <object_name>
            f.function_attribute
        <expression_value>
            1
        <docstring lineno="34">
            f.function_attribute docstring
'''],
]

"""
['''\
''',
'''\
'''],
"""

if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
