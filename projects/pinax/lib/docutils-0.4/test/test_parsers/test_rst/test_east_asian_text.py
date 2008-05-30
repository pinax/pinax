#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Author: David Goodger
# Contact: goodger@python.org
# Revision: $Revision: 4152 $
# Date: $Date: 2005-12-08 00:46:30 +0100 (Thu, 08 Dec 2005) $
# Copyright: This module has been placed in the public domain.

"""
Tests for East Asian text with double-width characters.
"""

from __init__ import DocutilsTestSupport

import unicodedata
try:
    east_asian_width = unicodedata.east_asian_width
except AttributeError:
    east_asian_width = None

def suite():
    s = DocutilsTestSupport.ParserTestSuite()
    s.generateTests(totest)
    return s

totest = {}

if not east_asian_width:
    print ('test_east_asian_text.py tests skipped; '
           'Python 2.4 or higher required.')
else:
    totest['double-width'] = [
[u"""\
タイトル1
=========

タイトル2
========
""",
u"""\
<document source="test data">
    <section ids="id1" names="タイトル1">
        <title>
            タイトル1
    <section ids="id2" names="タイトル2">
        <title>
            タイトル2
        <system_message level="2" line="5" source="test data" type="WARNING">
            <paragraph>
                Title underline too short.
            <literal_block xml:space="preserve">
                タイトル2
                ========
"""],
[ur"""
+-----------------------+
| * ヒョウ:ダイ1ギョウ  |
| * ダイ2ギョウ         |
+-----------------------+
| \* ダイ1ギョウ        |
| * ダイ2ギョウ         |
+-----------------------+
""",
u"""\
<document source="test data">
    <table>
        <tgroup cols="1">
            <colspec colwidth="23">
            <tbody>
                <row>
                    <entry>
                        <bullet_list bullet="*">
                            <list_item>
                                <paragraph>
                                    ヒョウ:ダイ1ギョウ
                            <list_item>
                                <paragraph>
                                    ダイ2ギョウ
                <row>
                    <entry>
                        <paragraph>
                            * ダイ1ギョウ
                            * ダイ2ギョウ
"""],
[u"""\
Complex spanning pattern (no edge knows all rows/cols):

+--------+---------------------+
| 北西・ | 北・北東セル        |
| 西セル +--------------+------+
|        | 真ん中のセル | 東・ |
+--------+--------------+ 南東 |
| 南西・南セル          | セル |
+-----------------------+------+
""",
u"""\
<document source="test data">
    <paragraph>
        Complex spanning pattern (no edge knows all rows/cols):
    <table>
        <tgroup cols="3">
            <colspec colwidth="8">
            <colspec colwidth="14">
            <colspec colwidth="6">
            <tbody>
                <row>
                    <entry morerows="1">
                        <paragraph>
                            北西・
                            西セル
                    <entry morecols="1">
                        <paragraph>
                            北・北東セル
                <row>
                    <entry>
                        <paragraph>
                            真ん中のセル
                    <entry morerows="1">
                        <paragraph>
                            東・
                            南東
                            セル
                <row>
                    <entry morecols="1">
                        <paragraph>
                            南西・南セル
"""],
[u"""\
=========  =========
ダイ1ラン  ダイ2ラン
=========  =========

========  =========
ダイ1ラン ダイ2ラン
========  =========
""",
u"""\
<document source="test data">
    <table>
        <tgroup cols="2">
            <colspec colwidth="9">
            <colspec colwidth="9">
            <tbody>
                <row>
                    <entry>
                        <paragraph>
                            ダイ1ラン
                    <entry>
                        <paragraph>
                            ダイ2ラン
    <system_message level="3" line="5" source="test data" type="ERROR">
        <paragraph>
            Malformed table.
            Text in column margin at line offset 1.
        <literal_block xml:space="preserve">
            ========  =========
            ダイ1ラン ダイ2ラン
            ========  =========
"""],
[u"""\
Some ambiguous-width characters:

= ===================================
© copyright sign
® registered sign
« left pointing guillemet
» right pointing guillemet
– en-dash
— em-dash
‘ single turned comma quotation mark 
’ single comma quotation mark 
‚ low single comma quotation mark 
“ double turned comma quotation mark 
” double comma quotation mark 
„ low double comma quotation mark 
† dagger
‡ double dagger
… ellipsis
™ trade mark sign
⇔ left-right double arrow
= ===================================
""",
u"""\
<document source="test data">
    <paragraph>
        Some ambiguous-width characters:
    <table>
        <tgroup cols="2">
            <colspec colwidth="1">
            <colspec colwidth="35">
            <tbody>
                <row>
                    <entry>
                        <paragraph>
                            \xa9
                    <entry>
                        <paragraph>
                            copyright sign
                <row>
                    <entry>
                        <paragraph>
                            \xae
                    <entry>
                        <paragraph>
                            registered sign
                <row>
                    <entry>
                        <paragraph>
                            \xab
                    <entry>
                        <paragraph>
                            left pointing guillemet
                <row>
                    <entry>
                        <paragraph>
                            \xbb
                    <entry>
                        <paragraph>
                            right pointing guillemet
                <row>
                    <entry>
                        <paragraph>
                            \\u2013
                    <entry>
                        <paragraph>
                            en-dash
                <row>
                    <entry>
                        <paragraph>
                            \\u2014
                    <entry>
                        <paragraph>
                            em-dash
                <row>
                    <entry>
                        <paragraph>
                            \\u2018
                    <entry>
                        <paragraph>
                            single turned comma quotation mark
                <row>
                    <entry>
                        <paragraph>
                            \\u2019
                    <entry>
                        <paragraph>
                            single comma quotation mark
                <row>
                    <entry>
                        <paragraph>
                            \\u201a
                    <entry>
                        <paragraph>
                            low single comma quotation mark
                <row>
                    <entry>
                        <paragraph>
                            \\u201c
                    <entry>
                        <paragraph>
                            double turned comma quotation mark
                <row>
                    <entry>
                        <paragraph>
                            \\u201d
                    <entry>
                        <paragraph>
                            double comma quotation mark
                <row>
                    <entry>
                        <paragraph>
                            \\u201e
                    <entry>
                        <paragraph>
                            low double comma quotation mark
                <row>
                    <entry>
                        <paragraph>
                            \\u2020
                    <entry>
                        <paragraph>
                            dagger
                <row>
                    <entry>
                        <paragraph>
                            \\u2021
                    <entry>
                        <paragraph>
                            double dagger
                <row>
                    <entry>
                        <paragraph>
                            \\u2026
                    <entry>
                        <paragraph>
                            ellipsis
                <row>
                    <entry>
                        <paragraph>
                            \\u2122
                    <entry>
                        <paragraph>
                            trade mark sign
                <row>
                    <entry>
                        <paragraph>
                            \\u21d4
                    <entry>
                        <paragraph>
                            left-right double arrow
"""],
]
'''
[u"""\
""",
u"""\
"""],
'''


if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
