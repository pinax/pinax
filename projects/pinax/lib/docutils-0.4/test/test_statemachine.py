#! /usr/bin/env python

# Author: David Goodger
# Contact: goodger@users.sourceforge.net
# Revision: $Revision: 917 $
# Date: $Date: 2002-11-08 02:38:11 +0100 (Fri, 08 Nov 2002) $
# Copyright: This module has been placed in the public domain.

"""
Test module for statemachine.py.
"""

import unittest
import sys
import re
from DocutilsTestSupport import statemachine


debug = 0
testtext = statemachine.string2lines("""\
First paragraph.

- This is a bullet list. First list item.
  Second line of first para.

  Second para.

      block quote

- Second list item. Example::

        a
      literal
           block

Last paragraph.""")
expected = ('StateMachine1 text1 blank1 bullet1 known_indent1 '
            'StateMachine2 text2 text2 blank2 text2 blank2 indent2 '
            'StateMachine3 text3 blank3 finished3 finished2 '
            'bullet1 known_indent1 '
            'StateMachine2 text2 blank2 literalblock2(4) finished2 '
            'text1 finished1').split()
para1 = testtext[:2]
item1 = [line[2:] for line in testtext[2:9]]
item2 = [line[2:] for line in testtext[9:-1]]
lbindent = 6
literalblock = [line[lbindent:] for line in testtext[11:-1]]
para2 = testtext[-1]


class MockState(statemachine.StateWS):

    patterns = {'bullet': re.compile(r'- '),
                'text': ''}
    initial_transitions = ['bullet', ['text']]
    levelholder = [0]

    def bof(self, context):
        self.levelholder[0] += 1
        self.level = self.levelholder[0]
        if self.debug: print >>sys.stderr, 'StateMachine%s' % self.level
        return [], ['StateMachine%s' % self.level]

    def blank(self, match, context, next_state):
        result = ['blank%s' % self.level]
        if self.debug: print >>sys.stderr, 'blank%s' % self.level
        if context and context[-1] and context[-1][-2:] == '::':
            result.extend(self.literalblock())
        return [], None, result

    def indent(self, match, context, next_state):
        if self.debug: print >>sys.stderr, 'indent%s' % self.level
        context, next_state, result = statemachine.StateWS.indent(
              self, match, context, next_state)
        return context, next_state, ['indent%s' % self.level] + result

    def known_indent(self, match, context, next_state):
        if self.debug: print >>sys.stderr, 'known_indent%s' % self.level
        context, next_state, result = statemachine.StateWS.known_indent(
              self, match, context, next_state)
        return context, next_state, ['known_indent%s' % self.level] + result

    def bullet(self, match, context, next_state):
        if self.debug: print >>sys.stderr, 'bullet%s' % self.level
        context, next_state, result \
              = self.known_indent(match, context, next_state)
        return [], next_state, ['bullet%s' % self.level] + result

    def text(self, match, context, next_state):
        if self.debug: print >>sys.stderr, 'text%s' % self.level
        return [match.string], next_state, ['text%s' % self.level]

    def literalblock(self):
        indented, indent, offset, good = self.state_machine.get_indented()
        if self.debug: print >>sys.stderr, 'literalblock%s(%s)' % (self.level,
                                                                   indent)
        return ['literalblock%s(%s)' % (self.level, indent)]

    def eof(self, context):
        self.levelholder[0] -= 1
        if self.debug: print >>sys.stderr, 'finished%s' % self.level
        return ['finished%s' % self.level]


class EmptySMTests(unittest.TestCase):

    def setUp(self):
        self.sm = statemachine.StateMachine(
              state_classes=[], initial_state='State')
        self.sm.debug = debug

    def test_add_state(self):
        self.sm.add_state(statemachine.State)
        self.assert_(len(self.sm.states) == 1)
        self.assertRaises(statemachine.DuplicateStateError, self.sm.add_state,
                          statemachine.State)
        self.sm.add_state(statemachine.StateWS)
        self.assert_(len(self.sm.states) == 2)

    def test_add_states(self):
        self.sm.add_states((statemachine.State, statemachine.StateWS))
        self.assertEqual(len(self.sm.states), 2)

    def test_get_state(self):
        self.assertRaises(statemachine.UnknownStateError, self.sm.get_state)
        self.sm.add_states((statemachine.State, statemachine.StateWS))
        self.assertRaises(statemachine.UnknownStateError, self.sm.get_state,
                          'unknownState')
        self.assert_(isinstance(self.sm.get_state('State'),
                                statemachine.State))
        self.assert_(isinstance(self.sm.get_state('StateWS'),
                                statemachine.State))
        self.assertEqual(self.sm.current_state, 'StateWS')


class EmptySMWSTests(EmptySMTests):

    def setUp(self):
        self.sm = statemachine.StateMachineWS(
              state_classes=[], initial_state='State')
        self.sm.debug = debug


class SMWSTests(unittest.TestCase):

    def setUp(self):
        self.sm = statemachine.StateMachineWS([MockState], 'MockState',
                                              debug=debug)
        self.sm.debug = debug
        self.sm.states['MockState'].levelholder[0] = 0

    def tearDown(self):
        self.sm.unlink()

    def test___init__(self):
        self.assertEquals(self.sm.states.keys(), ['MockState'])
        self.assertEquals(len(self.sm.states['MockState'].transitions), 4)

    def test_get_indented(self):
        self.sm.input_lines = statemachine.StringList(testtext)
        self.sm.line_offset = -1
        self.sm.next_line(3)
        indented, offset, good = self.sm.get_known_indented(2)
        self.assertEquals(indented, item1)
        self.assertEquals(offset, len(para1))
        self.failUnless(good)
        self.sm.next_line()
        indented, offset, good = self.sm.get_known_indented(2)
        self.assertEquals(indented, item2)
        self.assertEquals(offset, len(para1) + len(item1))
        self.failUnless(good)
        self.sm.previous_line(3)
        if self.sm.debug:
            print '\ntest_get_indented: self.sm.line:\n', self.sm.line
        indented, indent, offset, good = self.sm.get_indented()
        if self.sm.debug:
            print '\ntest_get_indented: indented:\n', indented
        self.assertEquals(indent, lbindent)
        self.assertEquals(indented, literalblock)
        self.assertEquals(offset, (len(para1) + len(item1) + len(item2)
                                   - len(literalblock)))
        self.failUnless(good)

    def test_get_text_block(self):
        self.sm.input_lines = statemachine.StringList(testtext)
        self.sm.line_offset = -1
        self.sm.next_line()
        textblock = self.sm.get_text_block()
        self.assertEquals(textblock, testtext[:1])
        self.sm.next_line(2)
        textblock = self.sm.get_text_block()
        self.assertEquals(textblock, testtext[2:4])

    def test_get_text_block_flush_left(self):
        self.sm.input_lines = statemachine.StringList(testtext)
        self.sm.line_offset = -1
        self.sm.next_line()
        textblock = self.sm.get_text_block(flush_left=1)
        self.assertEquals(textblock, testtext[:1])
        self.sm.next_line(2)
        self.assertRaises(statemachine.UnexpectedIndentationError,
                          self.sm.get_text_block, flush_left=1)

    def test_run(self):
        self.assertEquals(self.sm.run(testtext), expected)


class EmptyClass:
    pass


class EmptyStateTests(unittest.TestCase):

    def setUp(self):
        self.state = statemachine.State(EmptyClass(), debug=debug)
        self.state.patterns = {'nop': 'dummy',
                               'nop2': 'dummy',
                               'nop3': 'dummy',
                               'bogus': 'dummy'}
        self.state.nop2 = self.state.nop3 = self.state.nop

    def test_add_transitions(self):
        self.assertEquals(len(self.state.transitions), 0)
        self.state.add_transitions(['None'], {'None': None})
        self.assertEquals(len(self.state.transitions), 1)
        self.assertRaises(statemachine.UnknownTransitionError,
                          self.state.add_transitions, ['bogus'], {})
        self.assertRaises(statemachine.DuplicateTransitionError,
                          self.state.add_transitions, ['None'],
                          {'None': None})

    def test_add_transition(self):
        self.assertEquals(len(self.state.transitions), 0)
        self.state.add_transition('None', None)
        self.assertEquals(len(self.state.transitions), 1)
        self.assertRaises(statemachine.DuplicateTransitionError,
                          self.state.add_transition, 'None', None)

    def test_remove_transition(self):
        self.assertEquals(len(self.state.transitions), 0)
        self.state.add_transition('None', None)
        self.assertEquals(len(self.state.transitions), 1)
        self.state.remove_transition('None')
        self.assertEquals(len(self.state.transitions), 0)
        self.assertRaises(statemachine.UnknownTransitionError,
                          self.state.remove_transition, 'None')

    def test_make_transition(self):
        dummy = re.compile('dummy')
        self.assertEquals(self.state.make_transition('nop', 'bogus'),
                          (dummy, self.state.nop, 'bogus'))
        self.assertEquals(self.state.make_transition('nop'),
                          (dummy, self.state.nop,
                           self.state.__class__.__name__))
        self.assertRaises(statemachine.TransitionPatternNotFound,
                          self.state.make_transition, 'None')
        self.assertRaises(statemachine.TransitionMethodNotFound,
                          self.state.make_transition, 'bogus')

    def test_make_transitions(self):
        dummy = re.compile('dummy')
        self.assertEquals(self.state.make_transitions(('nop', ['nop2'],
                                                       ('nop3', 'bogus'))),
                          (['nop', 'nop2', 'nop3'],
                           {'nop': (dummy, self.state.nop,
                                    self.state.__class__.__name__),
                            'nop2': (dummy, self.state.nop2,
                                     self.state.__class__.__name__),
                            'nop3': (dummy, self.state.nop3, 'bogus')}))


class MiscTests(unittest.TestCase):

    s2l_string = "hello\tthere\thow are\tyou?\n\tI'm fine\tthanks.\n"
    s2l_expected = ['hello   there   how are you?',
                    "        I'm fine        thanks."]
    def test_string2lines(self):
        self.assertEquals(statemachine.string2lines(self.s2l_string),
                          self.s2l_expected)


if __name__ == '__main__':
    unittest.main()
