#!/usr/bin/env python

# Author: Garth Kidd
# Contact: garth@deadlybloodyserious.com
# Author: David Goodger
# Contact: goodger@users.sourceforge.net
# Revision: $Revision: 3103 $
# Date: $Date: 2005-03-23 23:21:20 +0100 (Wed, 23 Mar 2005) $
# Copyright: This module has been placed in the public domain.

try:
    import locale
    locale.setlocale(locale.LC_ALL, '')
except:
    pass

import sys
import os
import getopt
import docutils
from docutils.frontend import OptionParser
from docutils.utils import new_document
from docutils.parsers.rst import Parser


usage_header = """\
quicktest.py: quickly test the restructuredtext parser.

Usage::

    quicktest.py [options] [<source> [<destination>]]

``source`` is the name of the file to use as input (default is stdin).
``destination`` is the name of the file to create as output (default is
stdout).

Options:
"""

options = [('pretty', 'p',
            'output pretty pseudo-xml: no "&abc;" entities (default)'),
           ('test', 't', 'output test-ready data (input & expected output, '
            'ready to be copied to a parser test module)'),
           ('rawxml', 'r', 'output raw XML'),
           ('styledxml=', 's', 'output raw XML with XSL style sheet '
            'reference (filename supplied in the option argument)'),
           ('xml', 'x', 'output pretty XML (indented)'),
           ('attributes', 'A', 'dump document attributes after processing'),
           ('debug', 'd', 'debug mode (lots of output)'),
           ('version', 'V', 'show Docutils version then exit'),
           ('help', 'h', 'show help text then exit')]
"""See ``distutils.fancy_getopt.FancyGetopt.__init__`` for a description of
the data structure: (long option, short option, description)."""

def usage():
    print usage_header
    for longopt, shortopt, description in options:
        if longopt[-1:] == '=':
            opts = '-%s arg, --%sarg' % (shortopt, longopt)
        else:
            opts = '-%s, --%s' % (shortopt, longopt)
        print '%-15s' % opts,
        if len(opts) > 14:
            print '%-16s' % '\n',
        while len(description) > 60:
            limit = description.rindex(' ', 0, 60)
            print description[:limit].strip()
            description = description[limit + 1:]
            print '%-15s' % ' ',
        print description

def _pretty(input, document, optargs):
    return document.pformat()

def _rawxml(input, document, optargs):
    return document.asdom().toxml()

def _styledxml(input, document, optargs):
    docnode = document.asdom().childNodes[0]
    return '%s\n%s\n%s' % (
          '<?xml version="1.0" encoding="ISO-8859-1"?>',
          '<?xml-stylesheet type="text/xsl" href="%s"?>'
          % optargs['styledxml'], docnode.toxml())

def _prettyxml(input, document, optargs):
    return document.asdom().toprettyxml('    ', '\n')

def _test(input, document, optargs):
    tq = '"""'
    output = document.pformat()         # same as _pretty()
    return """\
    totest['change_this_test_name'] = [
[%s\\
%s
%s,
%s\\
%s
%s],
]
""" % ( tq, escape(input.rstrip()), tq, tq, escape(output.rstrip()), tq )

def escape(text):
    """
    Return `text` in triple-double-quoted Python string form.
    """
    text = text.replace('\\', '\\\\')   # escape backslashes
    text = text.replace('"""', '""\\"') # break up triple-double-quotes
    text = text.replace(' \n', ' \\n\\\n') # protect trailing whitespace
    return text

_outputFormatters = {
    'rawxml': _rawxml,
    'styledxml': _styledxml,
    'xml': _prettyxml,
    'pretty' : _pretty,
    'test': _test
    }

def format(outputFormat, input, document, optargs):
    formatter = _outputFormatters[outputFormat]
    return formatter(input, document, optargs)

def getArgs():
    if os.name == 'mac' and len(sys.argv) <= 1:
        return macGetArgs()
    else:
        return posixGetArgs(sys.argv[1:])

def posixGetArgs(argv):
    outputFormat = 'pretty'
    # convert fancy_getopt style option list to getopt.getopt() arguments
    shortopts = ''.join([option[1] + ':' * (option[0][-1:] == '=')
                         for option in options if option[1]])
    longopts = [option[0] for option in options if option[0]]
    try:
        opts, args = getopt.getopt(argv, shortopts, longopts)
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    optargs = {'debug': 0, 'attributes': 0}
    for o, a in opts:
        if o in ['-h', '--help']:
            usage()
            sys.exit()
        elif o in ['-V', '--version']:
            print >>sys.stderr, ('quicktest.py (Docutils %s)'
                                 % docutils.__version__)
            sys.exit()
        elif o in ['-r', '--rawxml']:
            outputFormat = 'rawxml'
        elif o in ['-s', '--styledxml']:
            outputFormat = 'styledxml'
            optargs['styledxml'] = a
        elif o in ['-x', '--xml']:
            outputFormat = 'xml'
        elif o in ['-p', '--pretty']:
            outputFormat = 'pretty'
        elif o in ['-t', '--test']:
            outputFormat = 'test'
        elif o in ['--attributes', '-A']:
            optargs['attributes'] = 1
        elif o in ['-d', '--debug']:
            optargs['debug'] = 1
        else:
            raise getopt.GetoptError, "getopt should have saved us!"
    if len(args) > 2:
        print 'Maximum 2 arguments allowed.'
        usage()
        sys.exit(1)
    inputFile = sys.stdin
    outputFile = sys.stdout
    if args:
        inputFile = open(args.pop(0))
    if args:
        outputFile = open(args.pop(0), 'w')
    return inputFile, outputFile, outputFormat, optargs

def macGetArgs():
    import EasyDialogs
    EasyDialogs.Message("""\
Use the next dialog to build a command line:

1. Choose an output format from the [Option] list 
2. Click [Add]
3. Choose an input file: [Add existing file...]
4. Save the output: [Add new file...]
5. [OK]""")
    optionlist = [(longopt, description)
                  for (longopt, shortopt, description) in options]
    argv = EasyDialogs.GetArgv(optionlist=optionlist, addfolder=0)
    return posixGetArgs(argv)

def main():
    # process cmdline arguments:
    inputFile, outputFile, outputFormat, optargs = getArgs()
    settings = OptionParser(components=(Parser,)).get_default_values()
    settings.debug = optargs['debug']
    parser = Parser()
    input = inputFile.read()
    document = new_document(inputFile.name, settings)
    parser.parse(input, document)
    output = format(outputFormat, input, document, optargs)
    outputFile.write(output)
    if optargs['attributes']:
        import pprint
        pprint.pprint(document.__dict__)


if __name__ == '__main__':
    sys.stderr = sys.stdout
    main()
