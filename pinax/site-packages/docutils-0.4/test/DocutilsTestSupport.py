# Authors:  David Goodger; Garth Kidd
# Contact: goodger@users.sourceforge.net
# Revision: $Revision: 4258 $
# Date: $Date: 2006-01-09 04:29:23 +0100 (Mon, 09 Jan 2006) $
# Copyright: This module has been placed in the public domain.

"""
Exports the following:

:Modules:
    - `statemachine` is 'docutils.statemachine'
    - `nodes` is 'docutils.nodes'
    - `urischemes` is 'docutils.urischemes'
    - `utils` is 'docutils.utils'
    - `transforms` is 'docutils.transforms'
    - `states` is 'docutils.parsers.rst.states'
    - `tableparser` is 'docutils.parsers.rst.tableparser'

:Classes:
    - `StandardTestCase`
    - `CustomTestCase`
    - `CustomTestSuite`
    - `TransformTestCase`
    - `TransformTestSuite`
    - `ParserTestCase`
    - `ParserTestSuite`
    - `ParserTransformTestCase`
    - `PEPParserTestCase`
    - `PEPParserTestSuite`
    - `GridTableParserTestCase`
    - `GridTableParserTestSuite`
    - `SimpleTableParserTestCase`
    - `SimpleTableParserTestSuite`
    - `WriterPublishTestCase`
    - `LatexWriterPublishTestCase`
    - `PseudoXMLWriterPublishTestCase`
    - `HtmlWriterPublishTestCase`
    - `PublishTestSuite`
    - `HtmlFragmentTestSuite`
    - `DevNull` (output sink)
"""
__docformat__ = 'reStructuredText'

import sys
import os

testroot = os.path.abspath(os.path.dirname(__file__) or os.curdir)
os.chdir(testroot)
sys.path.insert(0, os.path.normpath(os.path.join(testroot, '..')))
sys.path.insert(0, testroot)
sys.path.append(os.path.normpath(os.path.join(testroot, '..', 'extras')))

import unittest
import docutils_difflib
import inspect
from pprint import pformat
from types import UnicodeType, StringType
import package_unittest
import docutils
import docutils.core
from docutils import frontend, nodes, statemachine, urischemes, utils
from docutils.transforms import universal
from docutils.parsers import rst
from docutils.parsers.rst import states, tableparser, roles, languages
from docutils.readers import standalone, pep
from docutils.statemachine import StringList, string2lines

try:
    from docutils.readers.python import moduleparser
    from tokenize import generate_tokens
    del generate_tokens
except ImportError:      # moduleparser depends on modules added in Python 2.2
    moduleparser = None

try:
    import mypdb as pdb
except:
    import pdb


# Hack to make repr(StringList) look like repr(list):
StringList.__repr__ = StringList.__str__


class DevNull:

    """Output sink."""

    def write(self, string):
        pass

    def close(self):
        pass


class StandardTestCase(unittest.TestCase):

    """
    Helper class, providing the same interface as unittest.TestCase,
    but with useful setUp and comparison methods.
    """

    def setUp(self):
        os.chdir(testroot)

    def failUnlessEqual(self, first, second, msg=None):
        """Fail if the two objects are unequal as determined by the '=='
           operator.
        """
        if not first == second:
            raise self.failureException, \
                  (msg or '%s != %s' % _format_str(first, second))

    def failIfEqual(self, first, second, msg=None):
        """Fail if the two objects are equal as determined by the '=='
           operator.
        """
        if first == second:
            raise self.failureException, \
                  (msg or '%s == %s' % _format_str(first, second))

    # Synonyms for assertion methods

    assertEqual = assertEquals = failUnlessEqual

    assertNotEqual = assertNotEquals = failIfEqual


class CustomTestCase(StandardTestCase):
    
    """
    Helper class, providing extended functionality over unittest.TestCase.

    The methods failUnlessEqual and failIfEqual have been overwritten
    to provide better support for multi-line strings.  Furthermore,
    see the compare_output method and the parameter list of __init__.
    """

    compare = docutils_difflib.Differ().compare
    """Comparison method shared by all subclasses."""

    def __init__(self, method_name, input, expected, id, run_in_debugger=0,
                 suite_settings=None):
        """
        Initialise the CustomTestCase.

        Arguments:

        method_name -- name of test method to run.
        input -- input to the parser.
        expected -- expected output from the parser.
        id -- unique test identifier, used by the test framework.
        run_in_debugger -- if true, run this test under the pdb debugger.
        suite_settings -- settings overrides for this test suite.
        """
        self.id = id
        self.input = input
        self.expected = expected
        self.run_in_debugger = run_in_debugger
        self.suite_settings = suite_settings or {}
        
        # Ring your mother.
        unittest.TestCase.__init__(self, method_name)

    def __str__(self):
        """
        Return string conversion. Overridden to give test id, in addition to
        method name.
        """
        return '%s; %s' % (self.id, unittest.TestCase.__str__(self))

    def __repr__(self):
        return "<%s %s>" % (self.id, unittest.TestCase.__repr__(self))

    def clear_roles(self):
        # Language-specific roles and roles added by the
        # "default-role" and "role" directives are currently stored
        # globally in the roles._roles dictionary.  This workaround
        # empties that dictionary.
        roles._roles = {}

    def setUp(self):
        StandardTestCase.setUp(self)
        self.clear_roles()

    def compare_output(self, input, output, expected):
        """`input`, `output`, and `expected` should all be strings."""
        if isinstance(input, UnicodeType):
            input = input.encode('raw_unicode_escape')
        if isinstance(output, UnicodeType):
            output = output.encode('raw_unicode_escape')
        if isinstance(expected, UnicodeType):
            expected = expected.encode('raw_unicode_escape')
        try:
            self.assertEquals(output, expected)
        except AssertionError, error:
            print >>sys.stderr, '\n%s\ninput:' % (self,)
            print >>sys.stderr, input
            try:
                comparison = ''.join(self.compare(expected.splitlines(1),
                                                  output.splitlines(1)))
                print >>sys.stderr, '-: expected\n+: output'
                print >>sys.stderr, comparison
            except AttributeError:      # expected or output not a string
                # alternative output for non-strings:
                print >>sys.stderr, 'expected: %r' % expected
                print >>sys.stderr, 'output:   %r' % output
            raise error


class CustomTestSuite(unittest.TestSuite):

    """
    A collection of CustomTestCases.

    Provides test suite ID generation and a method for adding test cases.
    """

    id = ''
    """Identifier for the TestSuite. Prepended to the
    TestCase identifiers to make identification easier."""

    next_test_case_id = 0
    """The next identifier to use for non-identified test cases."""

    def __init__(self, tests=(), id=None, suite_settings=None):
        """
        Initialize the CustomTestSuite.

        Arguments:

        id -- identifier for the suite, prepended to test cases.
        suite_settings -- settings overrides for this test suite.
        """
        unittest.TestSuite.__init__(self, tests)
        self.suite_settings = suite_settings or {}
        if id is None:
            mypath = os.path.abspath(
                sys.modules[CustomTestSuite.__module__].__file__)
            outerframes = inspect.getouterframes(inspect.currentframe())
            for outerframe in outerframes[1:]:
                if outerframe[3] != '__init__':
                    callerpath = outerframe[1]
                    if callerpath is None:
                        # It happens sometimes.  Why is a mystery.
                        callerpath = os.getcwd()
                    callerpath = os.path.abspath(callerpath)
                    break
            mydir, myname = os.path.split(mypath)
            if not mydir:
                mydir = os.curdir
            if callerpath.startswith(mydir):
                self.id = callerpath[len(mydir) + 1:] # caller's module
            else:
                self.id = callerpath
        else:
            self.id = id

    def addTestCase(self, test_case_class, method_name, input, expected,
                    id=None, run_in_debugger=0, **kwargs):
        """
        Create a CustomTestCase in the CustomTestSuite.
        Also return it, just in case.

        Arguments:

        test_case_class -- the CustomTestCase to add
        method_name -- a string; CustomTestCase.method_name is the test
        input -- input to the parser.
        expected -- expected output from the parser.
        id -- unique test identifier, used by the test framework.
        run_in_debugger -- if true, run this test under the pdb debugger.
        """
        if id is None:                  # generate id if required
            id = self.next_test_case_id
            self.next_test_case_id += 1
        # test identifier will become suiteid.testid
        tcid = '%s: %s' % (self.id, id)
        # suite_settings may be passed as a parameter;
        # if not, set from attribute:
        kwargs.setdefault('suite_settings', self.suite_settings)
        # generate and add test case
        tc = test_case_class(method_name, input, expected, tcid,
                             run_in_debugger=run_in_debugger, **kwargs)
        self.addTest(tc)
        return tc

    def generate_no_tests(self, *args, **kwargs):
        pass


class TransformTestCase(CustomTestCase):

    """
    Output checker for the transform.

    Should probably be called TransformOutputChecker, but I can deal with
    that later when/if someone comes up with a category of transform test
    cases that have nothing to do with the input and output of the transform.
    """

    option_parser = frontend.OptionParser(components=(rst.Parser,))
    settings = option_parser.get_default_values()
    settings.report_level = 1
    settings.halt_level = 5
    settings.debug = package_unittest.debug
    settings.warning_stream = DevNull()
    unknown_reference_resolvers = ()

    def __init__(self, *args, **kwargs):
        self.transforms = kwargs['transforms']
        """List of transforms to perform for this test case."""

        self.parser = kwargs['parser']
        """Input parser for this test case."""

        del kwargs['transforms'], kwargs['parser'] # only wanted here
        CustomTestCase.__init__(self, *args, **kwargs)

    def supports(self, format):
        return 1

    def test_transforms(self):
        if self.run_in_debugger:
            pdb.set_trace()
        settings = self.settings.copy()
        settings.__dict__.update(self.suite_settings)
        document = utils.new_document('test data', settings)
        self.parser.parse(self.input, document)
        # Don't do a ``populate_from_components()`` because that would
        # enable the Transformer's default transforms.
        document.transformer.add_transforms(self.transforms)
        document.transformer.add_transform(universal.TestMessages)
        document.transformer.components['writer'] = self
        document.transformer.apply_transforms()
        output = document.pformat()
        self.compare_output(self.input, output, self.expected)

    def test_transforms_verbosely(self):
        if self.run_in_debugger:
            pdb.set_trace()
        print '\n', self.id
        print '-' * 70
        print self.input
        settings = self.settings.copy()
        settings.__dict__.update(self.suite_settings)
        document = utils.new_document('test data', settings)
        self.parser.parse(self.input, document)
        print '-' * 70
        print document.pformat()
        for transformClass in self.transforms:
            transformClass(document).apply()
        output = document.pformat()
        print '-' * 70
        print output
        self.compare_output(self.input, output, self.expected)


class TransformTestSuite(CustomTestSuite):

    """
    A collection of TransformTestCases.

    A TransformTestSuite instance manufactures TransformTestCases,
    keeps track of them, and provides a shared test fixture (a-la
    setUp and tearDown).
    """

    def __init__(self, parser, suite_settings=None):
        self.parser = parser
        """Parser shared by all test cases."""

        CustomTestSuite.__init__(self, suite_settings=suite_settings)

    def generateTests(self, dict, dictname='totest',
                      testmethod='test_transforms'):
        """
        Stock the suite with test cases generated from a test data dictionary.

        Each dictionary key (test type's name) maps to a tuple, whose
        first item is a list of transform classes and whose second
        item is a list of tests. Each test is a list: input, expected
        output, optional modifier. The optional third entry, a
        behavior modifier, can be 0 (temporarily disable this test) or
        1 (run this test under the pdb debugger). Tests should be
        self-documenting and not require external comments.
        """
        for name, (transforms, cases) in dict.items():
            for casenum in range(len(cases)):
                case = cases[casenum]
                run_in_debugger = 0
                if len(case)==3:
                    # TODO: (maybe) change the 3rd argument to a dict, so it
                    # can handle more cases by keyword ('disable', 'debug',
                    # 'settings'), here and in other generateTests methods.
                    # But there's also the method that
                    # HtmlPublishPartsTestSuite uses <DJG>
                    if case[2]:
                        run_in_debugger = 1
                    else:
                        continue
                self.addTestCase(
                      TransformTestCase, testmethod,
                      transforms=transforms, parser=self.parser,
                      input=case[0], expected=case[1],
                      id='%s[%r][%s]' % (dictname, name, casenum),
                      run_in_debugger=run_in_debugger)


class ParserTestCase(CustomTestCase):

    """
    Output checker for the parser.

    Should probably be called ParserOutputChecker, but I can deal with
    that later when/if someone comes up with a category of parser test
    cases that have nothing to do with the input and output of the parser.
    """

    parser = rst.Parser()
    """Parser shared by all ParserTestCases."""

    option_parser = frontend.OptionParser(components=(rst.Parser,))
    settings = option_parser.get_default_values()
    settings.report_level = 5
    settings.halt_level = 5
    settings.debug = package_unittest.debug

    def test_parser(self):
        if self.run_in_debugger:
            pdb.set_trace()
        settings = self.settings.copy()
        settings.__dict__.update(self.suite_settings)
        document = utils.new_document('test data', settings)
        self.parser.parse(self.input, document)
        output = document.pformat()
        self.compare_output(self.input, output, self.expected)


class ParserTestSuite(CustomTestSuite):

    """
    A collection of ParserTestCases.

    A ParserTestSuite instance manufactures ParserTestCases,
    keeps track of them, and provides a shared test fixture (a-la
    setUp and tearDown).
    """

    test_case_class = ParserTestCase

    def generateTests(self, dict, dictname='totest'):
        """
        Stock the suite with test cases generated from a test data dictionary.

        Each dictionary key (test type name) maps to a list of tests. Each
        test is a list: input, expected output, optional modifier. The
        optional third entry, a behavior modifier, can be 0 (temporarily
        disable this test) or 1 (run this test under the pdb debugger). Tests
        should be self-documenting and not require external comments.
        """
        for name, cases in dict.items():
            for casenum in range(len(cases)):
                case = cases[casenum]
                run_in_debugger = 0
                if len(case)==3:
                    if case[2]:
                        run_in_debugger = 1
                    else:
                        continue
                self.addTestCase(
                      self.test_case_class, 'test_parser',
                      input=case[0], expected=case[1],
                      id='%s[%r][%s]' % (dictname, name, casenum),
                      run_in_debugger=run_in_debugger)


class PEPParserTestCase(ParserTestCase):

    """PEP-specific parser test case."""

    parser = rst.Parser(rfc2822=1, inliner=rst.states.Inliner())
    """Parser shared by all PEPParserTestCases."""

    option_parser = frontend.OptionParser(components=(rst.Parser, pep.Reader))
    settings = option_parser.get_default_values()
    settings.report_level = 5
    settings.halt_level = 5
    settings.debug = package_unittest.debug


class PEPParserTestSuite(ParserTestSuite):

    """A collection of PEPParserTestCases."""

    test_case_class = PEPParserTestCase


class GridTableParserTestCase(CustomTestCase):

    parser = tableparser.GridTableParser()

    def test_parse_table(self):
        self.parser.setup(StringList(string2lines(self.input), 'test data'))
        try:
            self.parser.find_head_body_sep()
            self.parser.parse_table()
            output = self.parser.cells
        except Exception, details:
            output = '%s: %s' % (details.__class__.__name__, details)
        self.compare_output(self.input, pformat(output) + '\n',
                            pformat(self.expected) + '\n')

    def test_parse(self):
        try:
            output = self.parser.parse(StringList(string2lines(self.input),
                                                  'test data'))
        except Exception, details:
            output = '%s: %s' % (details.__class__.__name__, details)
        self.compare_output(self.input, pformat(output) + '\n',
                            pformat(self.expected) + '\n')


class GridTableParserTestSuite(CustomTestSuite):

    """
    A collection of GridTableParserTestCases.

    A GridTableParserTestSuite instance manufactures GridTableParserTestCases,
    keeps track of them, and provides a shared test fixture (a-la setUp and
    tearDown).
    """

    test_case_class = GridTableParserTestCase

    def generateTests(self, dict, dictname='totest'):
        """
        Stock the suite with test cases generated from a test data dictionary.

        Each dictionary key (test type name) maps to a list of tests. Each
        test is a list: an input table, expected output from parse_table(),
        expected output from parse(), optional modifier. The optional fourth
        entry, a behavior modifier, can be 0 (temporarily disable this test)
        or 1 (run this test under the pdb debugger). Tests should be
        self-documenting and not require external comments.
        """
        for name, cases in dict.items():
            for casenum in range(len(cases)):
                case = cases[casenum]
                run_in_debugger = 0
                if len(case) == 4:
                    if case[-1]:
                        run_in_debugger = 1
                    else:
                        continue
                self.addTestCase(self.test_case_class, 'test_parse_table',
                                 input=case[0], expected=case[1],
                                 id='%s[%r][%s]' % (dictname, name, casenum),
                                 run_in_debugger=run_in_debugger)
                self.addTestCase(self.test_case_class, 'test_parse',
                                 input=case[0], expected=case[2],
                                 id='%s[%r][%s]' % (dictname, name, casenum),
                                 run_in_debugger=run_in_debugger)


class SimpleTableParserTestCase(GridTableParserTestCase):

    parser = tableparser.SimpleTableParser()


class SimpleTableParserTestSuite(CustomTestSuite):

    """
    A collection of SimpleTableParserTestCases.
    """

    test_case_class = SimpleTableParserTestCase

    def generateTests(self, dict, dictname='totest'):
        """
        Stock the suite with test cases generated from a test data dictionary.

        Each dictionary key (test type name) maps to a list of tests. Each
        test is a list: an input table, expected output from parse(), optional
        modifier. The optional third entry, a behavior modifier, can be 0
        (temporarily disable this test) or 1 (run this test under the pdb
        debugger). Tests should be self-documenting and not require external
        comments.
        """
        for name, cases in dict.items():
            for casenum in range(len(cases)):
                case = cases[casenum]
                run_in_debugger = 0
                if len(case) == 3:
                    if case[-1]:
                        run_in_debugger = 1
                    else:
                        continue
                self.addTestCase(self.test_case_class, 'test_parse',
                                 input=case[0], expected=case[1],
                                 id='%s[%r][%s]' % (dictname, name, casenum),
                                 run_in_debugger=run_in_debugger)


class PythonModuleParserTestCase(CustomTestCase):

    def test_parser(self):
        if self.run_in_debugger:
            pdb.set_trace()
        module = moduleparser.parse_module(self.input, 'test data').pformat()
        output = str(module)
        self.compare_output(self.input, output, self.expected)

    def test_token_parser_rhs(self):
        if self.run_in_debugger:
            pdb.set_trace()
        tr = moduleparser.TokenParser(self.input)
        output = tr.rhs(1)
        self.compare_output(self.input, output, self.expected)


class PythonModuleParserTestSuite(CustomTestSuite):

    """
    A collection of PythonModuleParserTestCase.
    """

    notified = None

    def __init__(self, *args, **kwargs):
        if moduleparser is None:
            if not self.notified:
                print ('Tests of docutils.readers.python skipped; '
                       'Python 2.2 or higher required.')
                PythonModuleParserTestSuite.notified = 1
            self.generateTests = self.generate_no_tests
        CustomTestSuite.__init__(self, *args, **kwargs)

    def generateTests(self, dict, dictname='totest',
                      testmethod='test_parser'):
        """
        Stock the suite with test cases generated from a test data dictionary.

        Each dictionary key (test type's name) maps to a list of tests. Each
        test is a list: input, expected output, optional modifier. The
        optional third entry, a behavior modifier, can be 0 (temporarily
        disable this test) or 1 (run this test under the pdb debugger). Tests
        should be self-documenting and not require external comments.
        """
        for name, cases in dict.items():
            for casenum in range(len(cases)):
                case = cases[casenum]
                run_in_debugger = 0
                if len(case)==3:
                    if case[2]:
                        run_in_debugger = 1
                    else:
                        continue
                self.addTestCase(
                      PythonModuleParserTestCase, testmethod,
                      input=case[0], expected=case[1],
                      id='%s[%r][%s]' % (dictname, name, casenum),
                      run_in_debugger=run_in_debugger)


class WriterPublishTestCase(CustomTestCase, docutils.SettingsSpec):

    """
    Test case for publish.
    """

    settings_default_overrides = {'_disable_config': 1,
                                  'strict_visitor': 1}
    writer_name = '' # set in subclasses or constructor

    def __init__(self, *args, **kwargs):
        if kwargs.has_key('writer_name'):
            self.writer_name = kwargs['writer_name']
            del kwargs['writer_name']
        CustomTestCase.__init__(self, *args, **kwargs)

    def test_publish(self):
        if self.run_in_debugger:
            pdb.set_trace()
        output = docutils.core.publish_string(
              source=self.input,
              reader_name='standalone',
              parser_name='restructuredtext',
              writer_name=self.writer_name,
              settings_spec=self,
              settings_overrides=self.suite_settings)
        self.compare_output(self.input, output, self.expected)


class PublishTestSuite(CustomTestSuite):

    def __init__(self, writer_name, suite_settings=None):
        """
        `writer_name` is the name of the writer to use.
        """
        CustomTestSuite.__init__(self, suite_settings=suite_settings)
        self.test_class = WriterPublishTestCase
        self.writer_name = writer_name

    def generateTests(self, dict, dictname='totest'):
        for name, cases in dict.items():
            for casenum in range(len(cases)):
                case = cases[casenum]
                run_in_debugger = 0
                if len(case)==3:
                    if case[2]:
                        run_in_debugger = 1
                    else:
                        continue
                self.addTestCase(
                      self.test_class, 'test_publish',
                      input=case[0], expected=case[1],
                      id='%s[%r][%s]' % (dictname, name, casenum),
                      run_in_debugger=run_in_debugger,
                      # Passed to constructor of self.test_class:
                      writer_name=self.writer_name)


class HtmlPublishPartsTestSuite(CustomTestSuite):

    def generateTests(self, dict, dictname='totest'):
        for name, (settings_overrides, cases) in dict.items():
            settings = self.suite_settings.copy()
            settings.update(settings_overrides)
            for casenum in range(len(cases)):
                case = cases[casenum]
                run_in_debugger = 0
                if len(case)==3:
                    if case[2]:
                        run_in_debugger = 1
                    else:
                        continue
                self.addTestCase(
                      HtmlWriterPublishPartsTestCase, 'test_publish',
                      input=case[0], expected=case[1],
                      id='%s[%r][%s]' % (dictname, name, casenum),
                      run_in_debugger=run_in_debugger,
                      suite_settings=settings)


class HtmlWriterPublishPartsTestCase(WriterPublishTestCase):

    """
    Test case for HTML writer via the publish_parts interface.
    """

    writer_name = 'html'

    settings_default_overrides = \
        WriterPublishTestCase.settings_default_overrides.copy()
    settings_default_overrides['stylesheet'] = ''

    def test_publish(self):
        if self.run_in_debugger:
            pdb.set_trace()
        parts = docutils.core.publish_parts(
            source=self.input,
            reader_name='standalone',
            parser_name='restructuredtext',
            writer_name=self.writer_name,
            settings_spec=self,
            settings_overrides=self.suite_settings)
        output = self.format_output(parts)
        # interpolate standard variables:
        expected = self.expected % {'version': docutils.__version__}
        self.compare_output(self.input, output, expected)

    
    standard_content_type_template = ('<meta http-equiv="Content-Type"'
                                      ' content="text/html; charset=%s" />\n')
    standard_generator_template = (
        '<meta name="generator"'
        ' content="Docutils %s: http://docutils.sourceforge.net/" />\n')
    standard_html_meta_value = (
        standard_content_type_template
        + standard_generator_template % docutils.__version__)
    standard_meta_value = standard_html_meta_value % 'utf-8'
    standard_html_prolog = """\
<?xml version="1.0" encoding="%s" ?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
"""

    def format_output(self, parts):
        """Minimize & standardize the output."""
        # remove redundant parts:
        del parts['whole']
        assert parts['body'] == parts['fragment']
        del parts['body']
        # remove standard portions:
        parts['meta'] = parts['meta'].replace(self.standard_meta_value, '')
        parts['html_head'] = parts['html_head'].replace(
            self.standard_html_meta_value, '...')
        parts['html_prolog'] = parts['html_prolog'].replace(
            self.standard_html_prolog, '')
        # remove empty values:
        for key in parts.keys():
            if not parts[key]:
                del parts[key]
        # standard output format:
        keys = parts.keys()
        keys.sort()
        output = []
        for key in keys:
            output.append("%r: '''%s'''"
                          % (key, parts[key].encode('raw_unicode_escape')))
            if output[-1].endswith("\n'''"):
                output[-1] = output[-1][:-4] + "\\n'''"
        return '{' + ',\n '.join(output) + '}\n'


def exception_data(code):
    """
    Execute `code` and return the resulting exception, the exception arguments,
    and the formatted exception string.
    """
    try:
        exec(code)
    except Exception, detail:
        return (detail, detail.args,
                '%s: %s' % (detail.__class__.__name__, detail))


def _format_str(*args):
    r"""
    Return a tuple containing representations of all args.

    Same as map(repr, args) except that it returns multi-line
    representations for strings containing newlines, e.g.::

        '''\
        foo  \n\
        bar

        baz'''

    instead of::

        'foo  \nbar\n\nbaz'

    This is a helper function for CustomTestCase.
    """
    import re
    return_tuple = []
    for i in args:
        r = repr(i)
        if ( (isinstance(i, StringType) or isinstance(i, UnicodeType))
             and '\n' in i):
            stripped = ''
            if isinstance(i, UnicodeType):
                # stripped = 'u' or 'U'
                stripped = r[0]
                r = r[1:]
            # quote_char = "'" or '"'
            quote_char = r[0]
            assert quote_char in ("'", '"')
            assert r[0] == r[-1]
            r = r[1:-1]
            r = (stripped + 3 * quote_char + '\\\n' +
                 re.sub(r'(?<!\\)((\\\\)*)\\n', r'\1\n', r) +
                 3 * quote_char)
            r = re.sub(r' \n', r' \\n\\\n', r)
        return_tuple.append(r)
    return tuple(return_tuple)
