#! /usr/bin/env python

# Author: David Goodger
# Contact: goodger@python.org
# Revision: $Revision: 3532 $
# Date: $Date: 2005-06-20 20:59:29 +0200 (Mon, 20 Jun 2005) $
# Copyright: This program has been placed in the public domain.

"""
unicode2subfiles.py -- produce character entity files (reSructuredText
substitutions) from the W3C master unicode.xml file.

This program extracts character entity and entity set information from a
unicode.xml file and produces multiple reStructuredText files (in the current
directory) containing substitutions.  Entity sets are from ISO 8879 & ISO
9573-13 (combined), MathML, and HTML4.  One or two files are produced for each
entity set; a second file with a "-wide.txt" suffix is produced if there are
wide-Unicode characters in the set.

The input file, unicode.xml, is maintained as part of the MathML 2
Recommentation XML source, and is available from
<http://www.w3.org/2003/entities/xml/>.
"""

import sys
import os
import optparse
import re
from xml.parsers.expat import ParserCreate


usage_msg = """Usage: %s [unicode.xml]"""

def usage(prog, status=0, msg=None):
    print >>sys.stderr, usage_msg % prog
    if msg:
        print >>sys.stderr, msg
    sys.exit(status)

def main(argv=None):
    if argv is None:
        argv = sys.argv
    if len(argv) == 2:
        inpath = argv[1]
    elif len(argv) > 2:
        usage(argv[0], 2,
              'Too many arguments (%s): only 1 expected.' % (len(argv) - 1))
    else:
        inpath = 'unicode.xml'
    if not os.path.isfile(inpath):
        usage(argv[0], 1, 'No such file: "%s".' % inpath)
    infile = open(inpath)
    process(infile)

def process(infile):
    grouper = CharacterEntitySetExtractor(infile)
    grouper.group()
    grouper.write_sets()


class CharacterEntitySetExtractor:

    """
    Extracts character entity information from unicode.xml file, groups it by
    entity set, and writes out reStructuredText substitution files.
    """

    unwanted_entity_sets = ['stix',     # unknown, buggy set
                            'predefined']

    header = """\
.. This data file has been placed in the public domain.
.. Derived from the Unicode character mappings available from
   <http://www.w3.org/2003/entities/xml/>.
   Processed by unicode2rstsubs.py, part of Docutils:
   <http://docutils.sourceforge.net>.
"""

    def __init__(self, infile):
        self.infile = infile
        """Input unicode.xml file."""

        self.parser = self.setup_parser()
        """XML parser."""

        self.elements = []
        """Stack of element names.  Last is current element."""

        self.sets = {}
        """Mapping of charent set name to set dict."""

        self.charid = None
        """Current character's "id" attribute value."""

        self.descriptions = {}
        """Mapping of character ID to description."""

    def setup_parser(self):
        parser = ParserCreate()
        parser.StartElementHandler = self.StartElementHandler
        parser.EndElementHandler = self.EndElementHandler
        parser.CharacterDataHandler = self.CharacterDataHandler
        return parser

    def group(self):
        self.parser.ParseFile(self.infile)

    def StartElementHandler(self, name, attributes):
        self.elements.append(name)
        handler = name + '_start'
        if hasattr(self, handler):
            getattr(self, handler)(name, attributes)

    def EndElementHandler(self, name):
        assert self.elements[-1] == name, \
               'unknown end-tag %r (%r)' % (name, self.element)
        self.elements.pop()
        handler = name + '_end'
        if hasattr(self, handler):
            getattr(self, handler)(name)

    def CharacterDataHandler(self, data):
        handler = self.elements[-1] + '_data'
        if hasattr(self, handler):
            getattr(self, handler)(data)

    def character_start(self, name, attributes):
        self.charid = attributes['id']

    def entity_start(self, name, attributes):
        set = self.entity_set_name(attributes['set'])
        if not set:
            return
        if not self.sets.has_key(set):
            print 'bad set: %r' % set
            return
        entity = attributes['id']
        assert (not self.sets[set].has_key(entity)
                or self.sets[set][entity] == self.charid), \
                ('sets[%r][%r] == %r (!= %r)'
                 % (set, entity, self.sets[set][entity], self.charid))
        self.sets[set][entity] = self.charid

    def description_data(self, data):
        self.descriptions.setdefault(self.charid, '')
        self.descriptions[self.charid] += data

    entity_set_name_pat = re.compile(r'[0-9-]*(.+)$')
    """Pattern to strip ISO numbers off the beginning of set names."""

    def entity_set_name(self, name):
        """
        Return lowcased and standard-number-free entity set name.
        Return ``None`` for unwanted entity sets.
        """
        match = self.entity_set_name_pat.match(name)
        name = match.group(1).lower()
        if name in self.unwanted_entity_sets:
            return None
        self.sets.setdefault(name, {})
        return name

    def write_sets(self):
        sets = self.sets.keys()
        sets.sort()
        for set_name in sets:
            self.write_set(set_name)

    def write_set(self, set_name, wide=None):
        if wide:
            outname = set_name + '-wide.txt'
        else:
            outname = set_name + '.txt'
        outfile = open(outname, 'w')
        print 'writing file "%s"' % outname
        print >>outfile, self.header
        set = self.sets[set_name]
        entities = [(e.lower(), e) for e in set.keys()]
        entities.sort()
        longest = 0
        for _, entity_name in entities:
            longest = max(longest, len(entity_name))
        has_wide = None
        for _, entity_name in entities:
            has_wide = self.write_entity(
                set, set_name, entity_name, outfile, longest, wide) or has_wide
        if has_wide and not wide:
            self.write_set(set_name, 1)

    def write_entity(self, set, set_name, entity_name, outfile, longest,
                     wide=None):
        charid = set[entity_name]
        if not wide:
            for code in charid[1:].split('-'):
                if int(code, 16) > 0xFFFF:
                    return 1            # wide-Unicode character
        codes = ' '.join(['U+%s' % code for code in charid[1:].split('-')])
        print >>outfile, ('.. %-*s unicode:: %s .. %s'
                          % (longest + 2, '|' + entity_name + '|',
                             codes, self.descriptions[charid]))


if __name__ == '__main__':
    sys.exit(main())
