#!/usr/bin/python2.2

"""Test harness for diff_match_patch.py

Copyright 2006 Google Inc.
http://code.google.com/p/google-diff-match-patch/

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import unittest
import diff_match_patch as dmp_module
# Force a module reload so to make debugging easier (at least in PythonWin).
reload(dmp_module)

class DiffMatchPatchTest(unittest.TestCase):

  def setUp(self):
    "Test harness for dmp_module."
    self.dmp = dmp_module.diff_match_patch()

  def diff_rebuildtexts(self, diffs):
    # Construct the two texts which made up the diff originally.
    text1 = ""
    text2 = ""
    for x in xrange(0, len(diffs)):
      if diffs[x][0] != dmp_module.diff_match_patch.DIFF_INSERT:
        text1 += diffs[x][1]
      if diffs[x][0] != dmp_module.diff_match_patch.DIFF_DELETE:
        text2 += diffs[x][1]
    return (text1, text2)


  # DIFF TEST FUNCTIONS


  def testDiffCommonPrefix(self):
    # Detect and remove any common prefix.
    # Null case
    self.assertEquals(0, self.dmp.diff_commonPrefix("abc", "xyz"))

    # Non-null case
    self.assertEquals(4, self.dmp.diff_commonPrefix("1234abcdef", "1234xyz"))

  def testDiffCommonSuffix(self):
    # Detect and remove any common suffix.
    # Null case
    self.assertEquals(0, self.dmp.diff_commonSuffix("abc", "xyz"))

    # Non-null case
    self.assertEquals(4, self.dmp.diff_commonSuffix("abcdef1234", "xyz1234"))

  def testDiffHalfMatch(self):
    # Detect a halfmatch.
    # No match
    self.assertEquals(None, self.dmp.diff_halfMatch("1234567890", "abcdef"))

    # Single Match
    self.assertEquals(("12", "90", "a", "z", "345678"), self.dmp.diff_halfMatch("1234567890", "a345678z"))

    self.assertEquals(("a", "z", "12", "90", "345678"), self.dmp.diff_halfMatch("a345678z", "1234567890"))

    # Multiple Matches
    self.assertEquals(("12123", "123121", "a", "z", "1234123451234"), self.dmp.diff_halfMatch("121231234123451234123121", "a1234123451234z"))

    self.assertEquals(("", "-=-=-=-=-=", "x", "", "x-=-=-=-=-=-=-="), self.dmp.diff_halfMatch("x-=-=-=-=-=-=-=-=-=-=-=-=", "xx-=-=-=-=-=-=-="))

    self.assertEquals(("-=-=-=-=-=", "", "", "y", "-=-=-=-=-=-=-=y"), self.dmp.diff_halfMatch("-=-=-=-=-=-=-=-=-=-=-=-=y", "-=-=-=-=-=-=-=yy"))

  def testDiffLinesToChars(self):
    # Convert lines down to characters
    self.assertEquals(("\x01\x02\x01", "\x02\x01\x02", ["", "alpha\n", "beta\n"]), self.dmp.diff_linesToChars("alpha\nbeta\nalpha\n", "beta\nalpha\nbeta\n"))

    self.assertEquals(("", "\x01\x02\x03\x03", ["", "alpha\r\n", "beta\r\n", "\r\n"]), self.dmp.diff_linesToChars("", "alpha\r\nbeta\r\n\r\n\r\n"))

    self.assertEquals(("\x01", "\x02", ["", "a", "b"]), self.dmp.diff_linesToChars("a", "b"))

    # More than 256
    n = 300
    lineList = []
    charList = []
    for x in range(1, n + 1):
      lineList.append(str(x) + "\n")
      charList.append(unichr(x))
    self.assertEquals(n, len(lineList))
    lines = "".join(lineList)
    chars = "".join(charList)
    self.assertEquals(n, len(chars))
    lineList.insert(0, "")
    self.assertEquals((chars, "", lineList), self.dmp.diff_linesToChars(lines, ""))

  def testDiffCharsToLines(self):
    # Convert chars up to lines
    diffs = [(self.dmp.DIFF_EQUAL, "\x01\x02\x01"), (self.dmp.DIFF_INSERT, "\x02\x01\x02")]
    self.dmp.diff_charsToLines(diffs, ["", "alpha\n", "beta\n"])
    self.assertEquals([(self.dmp.DIFF_EQUAL, "alpha\nbeta\nalpha\n"), (self.dmp.DIFF_INSERT, "beta\nalpha\nbeta\n")], diffs)

    # More than 256
    n = 300
    lineList = []
    charList = []
    for x in range(1, n + 1):
      lineList.append(str(x) + "\n")
      charList.append(unichr(x))
    self.assertEquals(n, len(lineList))
    lines = "".join(lineList)
    chars = "".join(charList)
    self.assertEquals(n, len(chars))
    lineList.insert(0, "")
    diffs = [(self.dmp.DIFF_DELETE, chars)]
    self.dmp.diff_charsToLines(diffs, lineList)
    self.assertEquals([(self.dmp.DIFF_DELETE, lines)], diffs)

  def testDiffCleanupMerge(self):
    # Cleanup a messy diff
    # Null case
    diffs = []
    self.dmp.diff_cleanupMerge(diffs)
    self.assertEquals([], diffs)

    # No change case
    diffs = [(self.dmp.DIFF_EQUAL, "a"), (self.dmp.DIFF_DELETE, "b"), (self.dmp.DIFF_INSERT, "c")]
    self.dmp.diff_cleanupMerge(diffs)
    self.assertEquals([(self.dmp.DIFF_EQUAL, "a"), (self.dmp.DIFF_DELETE, "b"), (self.dmp.DIFF_INSERT, "c")], diffs)

    # Merge equalities
    diffs = [(self.dmp.DIFF_EQUAL, "a"), (self.dmp.DIFF_EQUAL, "b"), (self.dmp.DIFF_EQUAL, "c")]
    self.dmp.diff_cleanupMerge(diffs)
    self.assertEquals([(self.dmp.DIFF_EQUAL, "abc")], diffs)

    # Merge deletions
    diffs = [(self.dmp.DIFF_DELETE, "a"), (self.dmp.DIFF_DELETE, "b"), (self.dmp.DIFF_DELETE, "c")]
    self.dmp.diff_cleanupMerge(diffs)
    self.assertEquals([(self.dmp.DIFF_DELETE, "abc")], diffs)

    # Merge insertions
    diffs = [(self.dmp.DIFF_INSERT, "a"), (self.dmp.DIFF_INSERT, "b"), (self.dmp.DIFF_INSERT, "c")]
    self.dmp.diff_cleanupMerge(diffs)
    self.assertEquals([(self.dmp.DIFF_INSERT, "abc")], diffs)

    # Merge interweave
    diffs = [(self.dmp.DIFF_DELETE, "a"), (self.dmp.DIFF_INSERT, "b"), (self.dmp.DIFF_DELETE, "c"), (self.dmp.DIFF_INSERT, "d"), (self.dmp.DIFF_EQUAL, "e"), (self.dmp.DIFF_EQUAL, "f")]
    self.dmp.diff_cleanupMerge(diffs)
    self.assertEquals([(self.dmp.DIFF_DELETE, "ac"), (self.dmp.DIFF_INSERT, "bd"), (self.dmp.DIFF_EQUAL, "ef")], diffs)

    # Prefix and suffix detection
    diffs = [(self.dmp.DIFF_DELETE, "a"), (self.dmp.DIFF_INSERT, "abc"), (self.dmp.DIFF_DELETE, "dc")]
    self.dmp.diff_cleanupMerge(diffs)
    self.assertEquals([(self.dmp.DIFF_EQUAL, "a"), (self.dmp.DIFF_DELETE, "d"), (self.dmp.DIFF_INSERT, "b"), (self.dmp.DIFF_EQUAL, "c")], diffs)

    # Slide edit left
    diffs = [(self.dmp.DIFF_EQUAL, "a"), (self.dmp.DIFF_INSERT, "ba"), (self.dmp.DIFF_EQUAL, "c")]
    self.dmp.diff_cleanupMerge(diffs)
    self.assertEquals([(self.dmp.DIFF_INSERT, "ab"), (self.dmp.DIFF_EQUAL, "ac")], diffs)

    # Slide edit right
    diffs = [(self.dmp.DIFF_EQUAL, "c"), (self.dmp.DIFF_INSERT, "ab"), (self.dmp.DIFF_EQUAL, "a")]
    self.dmp.diff_cleanupMerge(diffs)
    self.assertEquals([(self.dmp.DIFF_EQUAL, "ca"), (self.dmp.DIFF_INSERT, "ba")], diffs)

    # Slide edit left recursive
    diffs = [(self.dmp.DIFF_EQUAL, "a"), (self.dmp.DIFF_DELETE, "b"), (self.dmp.DIFF_EQUAL, "c"), (self.dmp.DIFF_DELETE, "ac"), (self.dmp.DIFF_EQUAL, "x")]
    self.dmp.diff_cleanupMerge(diffs)
    self.assertEquals([(self.dmp.DIFF_DELETE, "abc"), (self.dmp.DIFF_EQUAL, "acx")], diffs)

    # Slide edit right recursive
    diffs = [(self.dmp.DIFF_EQUAL, "x"), (self.dmp.DIFF_DELETE, "ca"), (self.dmp.DIFF_EQUAL, "c"), (self.dmp.DIFF_DELETE, "b"), (self.dmp.DIFF_EQUAL, "a")]
    self.dmp.diff_cleanupMerge(diffs)
    self.assertEquals([(self.dmp.DIFF_EQUAL, "xca"), (self.dmp.DIFF_DELETE, "cba")], diffs)

  def testDiffCleanupSemanticLossless(self):
    # Slide diffs to match logical boundaries
    # Null case
    diffs = []
    self.dmp.diff_cleanupSemanticLossless(diffs)
    self.assertEquals([], diffs)

    # Blank lines
    diffs = [(self.dmp.DIFF_EQUAL, "AAA\r\n\r\nBBB"), (self.dmp.DIFF_INSERT, "\r\nDDD\r\n\r\nBBB"), (self.dmp.DIFF_EQUAL, "\r\nEEE")]
    self.dmp.diff_cleanupSemanticLossless(diffs)
    self.assertEquals([(self.dmp.DIFF_EQUAL, "AAA\r\n\r\n"), (self.dmp.DIFF_INSERT, "BBB\r\nDDD\r\n\r\n"), (self.dmp.DIFF_EQUAL, "BBB\r\nEEE")], diffs)

    # Line boundaries
    diffs = [(self.dmp.DIFF_EQUAL, "AAA\r\nBBB"), (self.dmp.DIFF_INSERT, " DDD\r\nBBB"), (self.dmp.DIFF_EQUAL, " EEE")]
    self.dmp.diff_cleanupSemanticLossless(diffs)
    self.assertEquals([(self.dmp.DIFF_EQUAL, "AAA\r\n"), (self.dmp.DIFF_INSERT, "BBB DDD\r\n"), (self.dmp.DIFF_EQUAL, "BBB EEE")], diffs)

    # Word boundaries
    diffs = [(self.dmp.DIFF_EQUAL, "The c"), (self.dmp.DIFF_INSERT, "ow and the c"), (self.dmp.DIFF_EQUAL, "at.")]
    self.dmp.diff_cleanupSemanticLossless(diffs)
    self.assertEquals([(self.dmp.DIFF_EQUAL, "The "), (self.dmp.DIFF_INSERT, "cow and the "), (self.dmp.DIFF_EQUAL, "cat.")], diffs)

    # Alphanumeric boundaries
    diffs = [(self.dmp.DIFF_EQUAL, "The-c"), (self.dmp.DIFF_INSERT, "ow-and-the-c"), (self.dmp.DIFF_EQUAL, "at.")]
    self.dmp.diff_cleanupSemanticLossless(diffs)
    self.assertEquals([(self.dmp.DIFF_EQUAL, "The-"), (self.dmp.DIFF_INSERT, "cow-and-the-"), (self.dmp.DIFF_EQUAL, "cat.")], diffs)

    # Hitting the start
    diffs = [(self.dmp.DIFF_EQUAL, "a"), (self.dmp.DIFF_DELETE, "a"), (self.dmp.DIFF_EQUAL, "ax")]
    self.dmp.diff_cleanupSemanticLossless(diffs)
    self.assertEquals([(self.dmp.DIFF_DELETE, "a"), (self.dmp.DIFF_EQUAL, "aax")], diffs)

    # Hitting the end
    diffs = [(self.dmp.DIFF_EQUAL, "xa"), (self.dmp.DIFF_DELETE, "a"), (self.dmp.DIFF_EQUAL, "a")]
    self.dmp.diff_cleanupSemanticLossless(diffs)
    self.assertEquals([(self.dmp.DIFF_EQUAL, "xaa"), (self.dmp.DIFF_DELETE, "a")], diffs)

  def testDiffCleanupSemantic(self):
    # Cleanup semantically trivial equalities
    # Null case
    diffs = []
    self.dmp.diff_cleanupSemantic(diffs)
    self.assertEquals([], diffs)

    # No elimination
    diffs = [(self.dmp.DIFF_DELETE, "a"), (self.dmp.DIFF_INSERT, "b"), (self.dmp.DIFF_EQUAL, "cd"), (self.dmp.DIFF_DELETE, "e")]
    self.dmp.diff_cleanupSemantic(diffs)
    self.assertEquals([(self.dmp.DIFF_DELETE, "a"), (self.dmp.DIFF_INSERT, "b"), (self.dmp.DIFF_EQUAL, "cd"), (self.dmp.DIFF_DELETE, "e")], diffs)

    # Simple elimination
    diffs = [(self.dmp.DIFF_DELETE, "a"), (self.dmp.DIFF_EQUAL, "b"), (self.dmp.DIFF_DELETE, "c")]
    self.dmp.diff_cleanupSemantic(diffs)
    self.assertEquals([(self.dmp.DIFF_DELETE, "abc"), (self.dmp.DIFF_INSERT, "b")], diffs)

    # Backpass elimination
    diffs = [(self.dmp.DIFF_DELETE, "ab"), (self.dmp.DIFF_EQUAL, "cd"), (self.dmp.DIFF_DELETE, "e"), (self.dmp.DIFF_EQUAL, "f"), (self.dmp.DIFF_INSERT, "g")]
    self.dmp.diff_cleanupSemantic(diffs)
    self.assertEquals([(self.dmp.DIFF_DELETE, "abcdef"), (self.dmp.DIFF_INSERT, "cdfg")], diffs)

    # Multiple eliminations
    diffs = [(self.dmp.DIFF_INSERT, "1"), (self.dmp.DIFF_EQUAL, "A"), (self.dmp.DIFF_DELETE, "B"), (self.dmp.DIFF_INSERT, "2"), (self.dmp.DIFF_EQUAL, "_"), (self.dmp.DIFF_INSERT, "1"), (self.dmp.DIFF_EQUAL, "A"), (self.dmp.DIFF_DELETE, "B"), (self.dmp.DIFF_INSERT, "2")]
    self.dmp.diff_cleanupSemantic(diffs)
    self.assertEquals([(self.dmp.DIFF_DELETE, "AB_AB"), (self.dmp.DIFF_INSERT, "1A2_1A2")], diffs)

    # Word boundaries
    diffs = [(self.dmp.DIFF_EQUAL, "The c"), (self.dmp.DIFF_DELETE, "ow and the c"), (self.dmp.DIFF_EQUAL, "at.")]
    self.dmp.diff_cleanupSemantic(diffs)
    self.assertEquals([(self.dmp.DIFF_EQUAL, "The "), (self.dmp.DIFF_DELETE, "cow and the "), (self.dmp.DIFF_EQUAL, "cat.")], diffs)

  def testDiffCleanupEfficiency(self):
    # Cleanup operationally trivial equalities
    self.dmp.Diff_EditCost = 4
    # Null case
    diffs = []
    self.dmp.diff_cleanupEfficiency(diffs)
    self.assertEquals([], diffs)

    # No elimination
    diffs = [(self.dmp.DIFF_DELETE, "ab"), (self.dmp.DIFF_INSERT, "12"), (self.dmp.DIFF_EQUAL, "wxyz"), (self.dmp.DIFF_DELETE, "cd"), (self.dmp.DIFF_INSERT, "34")]
    self.dmp.diff_cleanupEfficiency(diffs)
    self.assertEquals([(self.dmp.DIFF_DELETE, "ab"), (self.dmp.DIFF_INSERT, "12"), (self.dmp.DIFF_EQUAL, "wxyz"), (self.dmp.DIFF_DELETE, "cd"), (self.dmp.DIFF_INSERT, "34")], diffs)

    # Four-edit elimination
    diffs = [(self.dmp.DIFF_DELETE, "ab"), (self.dmp.DIFF_INSERT, "12"), (self.dmp.DIFF_EQUAL, "xyz"), (self.dmp.DIFF_DELETE, "cd"), (self.dmp.DIFF_INSERT, "34")]
    self.dmp.diff_cleanupEfficiency(diffs)
    self.assertEquals([(self.dmp.DIFF_DELETE, "abxyzcd"), (self.dmp.DIFF_INSERT, "12xyz34")], diffs)

    # Three-edit elimination
    diffs = [(self.dmp.DIFF_INSERT, "12"), (self.dmp.DIFF_EQUAL, "x"), (self.dmp.DIFF_DELETE, "cd"), (self.dmp.DIFF_INSERT, "34")]
    self.dmp.diff_cleanupEfficiency(diffs)
    self.assertEquals([(self.dmp.DIFF_DELETE, "xcd"), (self.dmp.DIFF_INSERT, "12x34")], diffs)

    # Backpass elimination
    diffs = [(self.dmp.DIFF_DELETE, "ab"), (self.dmp.DIFF_INSERT, "12"), (self.dmp.DIFF_EQUAL, "xy"), (self.dmp.DIFF_INSERT, "34"), (self.dmp.DIFF_EQUAL, "z"), (self.dmp.DIFF_DELETE, "cd"), (self.dmp.DIFF_INSERT, "56")]
    self.dmp.diff_cleanupEfficiency(diffs)
    self.assertEquals([(self.dmp.DIFF_DELETE, "abxyzcd"), (self.dmp.DIFF_INSERT, "12xy34z56")], diffs)

    # High cost elimination
    self.dmp.Diff_EditCost = 5
    diffs = [(self.dmp.DIFF_DELETE, "ab"), (self.dmp.DIFF_INSERT, "12"), (self.dmp.DIFF_EQUAL, "wxyz"), (self.dmp.DIFF_DELETE, "cd"), (self.dmp.DIFF_INSERT, "34")]
    self.dmp.diff_cleanupEfficiency(diffs)
    self.assertEquals([(self.dmp.DIFF_DELETE, "abwxyzcd"), (self.dmp.DIFF_INSERT, "12wxyz34")], diffs)
    self.dmp.Diff_EditCost = 4

  def testDiffPrettyHtml(self):
    # Pretty print
    diffs = [(self.dmp.DIFF_EQUAL, "a\n"), (self.dmp.DIFF_DELETE, "<B>b</B>"), (self.dmp.DIFF_INSERT, "c&d")]
    self.assertEquals("<SPAN TITLE=\"i=0\">a&para;<BR></SPAN><DEL STYLE=\"background:#FFE6E6;\" TITLE=\"i=2\">&lt;B&gt;b&lt;/B&gt;</DEL><INS STYLE=\"background:#E6FFE6;\" TITLE=\"i=2\">c&amp;d</INS>", self.dmp.diff_prettyHtml(diffs))

  def testDiffText(self):
    # Compute the source and destination texts
    diffs = [(self.dmp.DIFF_EQUAL, "jump"), (self.dmp.DIFF_DELETE, "s"), (self.dmp.DIFF_INSERT, "ed"), (self.dmp.DIFF_EQUAL, " over "), (self.dmp.DIFF_DELETE, "the"), (self.dmp.DIFF_INSERT, "a"), (self.dmp.DIFF_EQUAL, " lazy")]
    self.assertEquals("jumps over the lazy", self.dmp.diff_text1(diffs))

    self.assertEquals("jumped over a lazy", self.dmp.diff_text2(diffs))

  def testDiffDelta(self):
    # Convert a diff into delta string
    diffs = [(self.dmp.DIFF_EQUAL, "jump"), (self.dmp.DIFF_DELETE, "s"), (self.dmp.DIFF_INSERT, "ed"), (self.dmp.DIFF_EQUAL, " over "), (self.dmp.DIFF_DELETE, "the"), (self.dmp.DIFF_INSERT, "a"), (self.dmp.DIFF_EQUAL, " lazy"), (self.dmp.DIFF_INSERT, "old dog")]
    text1 = self.dmp.diff_text1(diffs)
    self.assertEquals("jumps over the lazy", text1)

    delta = self.dmp.diff_toDelta(diffs)
    self.assertEquals("=4\t-1\t+ed\t=6\t-3\t+a\t=5\t+old dog", delta)

    # Convert delta string into a diff
    self.assertEquals(diffs, self.dmp.diff_fromDelta(text1, delta))

    # Generates error (19 != 20)
    try:
      self.assertEquals(ValueError, self.dmp.diff_fromDelta(text1 + "x", delta))
    except ValueError:
      self.assertTrue(True)

    # Generates error (19 != 18)
    try:
      self.assertEquals(None, self.dmp.diff_fromDelta(text1[1:], delta))
    except ValueError:
      self.assertTrue(True)

    # Generates error (%c3%xy invalid Unicode)
    try:
      self.assertEquals(None, self.dmp.diff_fromDelta("", "+%c3xy"))
    except ValueError:
      self.assertTrue(True)

    # Test deltas with special characters
    diffs = [(self.dmp.DIFF_EQUAL, u"\u0680 \x00 \t %"), (self.dmp.DIFF_DELETE, u"\u0681 \x01 \n ^"), (self.dmp.DIFF_INSERT, u"\u0682 \x02 \\ |")]
    text1 = self.dmp.diff_text1(diffs)
    self.assertEquals(u"\u0680 \x00 \t %\u0681 \x01 \n ^", text1)

    delta = self.dmp.diff_toDelta(diffs)
    self.assertEquals("=7\t-7\t+%DA%82 %02 %5C %7C", delta)

    # Convert delta string into a diff
    self.assertEquals(diffs, self.dmp.diff_fromDelta(text1, delta))

    # Verify pool of unchanged characters
    diffs = [(self.dmp.DIFF_INSERT, "A-Z a-z 0-9 - _ . ! ~ * ' ( ) ; / ? : @ & = + $ , # ")]
    text2 = self.dmp.diff_text2(diffs)
    self.assertEquals("A-Z a-z 0-9 - _ . ! ~ * \' ( ) ; / ? : @ & = + $ , # ", text2)

    delta = self.dmp.diff_toDelta(diffs)
    self.assertEquals("+A-Z a-z 0-9 - _ . ! ~ * \' ( ) ; / ? : @ & = + $ , # ", delta)

    # Convert delta string into a diff
    self.assertEquals(diffs, self.dmp.diff_fromDelta("", delta))

  def testDiffXIndex(self):
    # Translate a location in text1 to text2
    self.assertEquals(5, self.dmp.diff_xIndex([(self.dmp.DIFF_DELETE, "a"), (self.dmp.DIFF_INSERT, "1234"), (self.dmp.DIFF_EQUAL, "xyz")], 2))

    # Translation on deletion
    self.assertEquals(1, self.dmp.diff_xIndex([(self.dmp.DIFF_EQUAL, "a"), (self.dmp.DIFF_DELETE, "1234"), (self.dmp.DIFF_EQUAL, "xyz")], 3))

  def testDiffPath(self):
    # Trace a path from back to front.
    # Single letters
    v_map = []
    v_map.append({(0,0):True})
    v_map.append({(0,1):True, (1,0):True})
    v_map.append({(0,2):True, (2,0):True, (2,2):True})
    v_map.append({(0,3):True, (2,3):True, (3,0):True, (4,3):True})
    v_map.append({(0,4):True, (2,4):True, (4,0):True, (4,4):True, (5,3):True})
    v_map.append({(0,5):True, (2,5):True, (4,5):True, (5,0):True, (6,3):True, (6,5):True})
    v_map.append({(0,6):True, (2,6):True, (4,6):True, (6,6):True, (7,5):True})
    self.assertEquals([(self.dmp.DIFF_INSERT, "W"), (self.dmp.DIFF_DELETE, "A"), (self.dmp.DIFF_EQUAL, "1"), (self.dmp.DIFF_DELETE, "B"), (self.dmp.DIFF_EQUAL, "2"), (self.dmp.DIFF_INSERT, "X"), (self.dmp.DIFF_DELETE, "C"), (self.dmp.DIFF_EQUAL, "3"), (self.dmp.DIFF_DELETE, "D")], self.dmp.diff_path1(v_map, "A1B2C3D", "W12X3"))

    v_map.pop()
    self.assertEquals([(self.dmp.DIFF_EQUAL, "4"), (self.dmp.DIFF_DELETE, "E"), (self.dmp.DIFF_INSERT, "Y"), (self.dmp.DIFF_EQUAL, "5"), (self.dmp.DIFF_DELETE, "F"), (self.dmp.DIFF_EQUAL, "6"), (self.dmp.DIFF_DELETE, "G"), (self.dmp.DIFF_INSERT, "Z")], self.dmp.diff_path2(v_map, "4E5F6G", "4Y56Z"))

    # Double letters
    v_map = []
    v_map.append({(0,0):True})
    v_map.append({(0,1):True, (1,0):True})
    v_map.append({(0,2):True, (1,1):True, (2,0):True})
    v_map.append({(0,3):True, (1,2):True, (2,1):True, (3,0):True})
    v_map.append({(0,4):True, (1,3):True, (3,1):True, (4,0):True, (4,4):True})
    self.assertEquals([(self.dmp.DIFF_INSERT, "WX"), (self.dmp.DIFF_DELETE, "AB"), (self.dmp.DIFF_EQUAL, "12")], self.dmp.diff_path1(v_map, "AB12", "WX12"))

    v_map = []
    v_map.append({(0,0):True})
    v_map.append({(0,1):True, (1,0):True})
    v_map.append({(1,1):True, (2,0):True, (2,4):True})
    v_map.append({(2,1):True, (2,5):True, (3,0):True, (3,4):True})
    v_map.append({(2,6):True, (3,5):True, (4,4):True})
    self.assertEquals([(self.dmp.DIFF_DELETE, "CD"), (self.dmp.DIFF_EQUAL, "34"), (self.dmp.DIFF_INSERT, "YZ")], self.dmp.diff_path2(v_map, "CD34", "34YZ"))

  def testDiffMain(self):
    # Perform a trivial diff
    # Null case
    self.assertEquals([(self.dmp.DIFF_EQUAL, "abc")], self.dmp.diff_main("abc", "abc", False))

    # Simple insertion
    self.assertEquals([(self.dmp.DIFF_EQUAL, "ab"), (self.dmp.DIFF_INSERT, "123"), (self.dmp.DIFF_EQUAL, "c")], self.dmp.diff_main("abc", "ab123c", False))

    # Simple deletion
    self.assertEquals([(self.dmp.DIFF_EQUAL, "a"), (self.dmp.DIFF_DELETE, "123"), (self.dmp.DIFF_EQUAL, "bc")], self.dmp.diff_main("a123bc", "abc", False))

    # Two insertions
    self.assertEquals([(self.dmp.DIFF_EQUAL, "a"), (self.dmp.DIFF_INSERT, "123"), (self.dmp.DIFF_EQUAL, "b"), (self.dmp.DIFF_INSERT, "456"), (self.dmp.DIFF_EQUAL, "c")], self.dmp.diff_main("abc", "a123b456c", False))

    # Two deletions
    self.assertEquals([(self.dmp.DIFF_EQUAL, "a"), (self.dmp.DIFF_DELETE, "123"), (self.dmp.DIFF_EQUAL, "b"), (self.dmp.DIFF_DELETE, "456"), (self.dmp.DIFF_EQUAL, "c")], self.dmp.diff_main("a123b456c", "abc", False))

    # Perform a real diff
    # Switch off the timeout.
    self.dmp.Diff_Timeout = 0
    self.dmp.Diff_DualThreshold = 32
    # Simple cases
    self.assertEquals([(self.dmp.DIFF_DELETE, "a"), (self.dmp.DIFF_INSERT, "b")], self.dmp.diff_main("a", "b", False))

    self.assertEquals([(self.dmp.DIFF_DELETE, "Apple"), (self.dmp.DIFF_INSERT, "Banana"), (self.dmp.DIFF_EQUAL, "s are a"), (self.dmp.DIFF_INSERT, "lso"), (self.dmp.DIFF_EQUAL, " fruit.")], self.dmp.diff_main("Apples are a fruit.", "Bananas are also fruit.", False))

    self.assertEquals([(self.dmp.DIFF_DELETE, "a"), (self.dmp.DIFF_INSERT, u"\u0680"), (self.dmp.DIFF_EQUAL, "x"), (self.dmp.DIFF_DELETE, "\t"), (self.dmp.DIFF_INSERT, u"\x00")], self.dmp.diff_main("ax\t", u"\u0680x\x00", False))

    # Overlaps
    self.assertEquals([(self.dmp.DIFF_DELETE, "1"), (self.dmp.DIFF_EQUAL, "a"), (self.dmp.DIFF_DELETE, "y"), (self.dmp.DIFF_EQUAL, "b"), (self.dmp.DIFF_DELETE, "2"), (self.dmp.DIFF_INSERT, "xab")], self.dmp.diff_main("1ayb2", "abxab", False))

    self.assertEquals([(self.dmp.DIFF_INSERT, "xaxcx"), (self.dmp.DIFF_EQUAL, "abc"), (self.dmp.DIFF_DELETE, "y")], self.dmp.diff_main("abcy", "xaxcxabc", False))

    # Sub-optimal double-ended diff.
    self.dmp.Diff_DualThreshold = 2
    self.assertEquals([(self.dmp.DIFF_INSERT, "x"), (self.dmp.DIFF_EQUAL, "a"), (self.dmp.DIFF_DELETE, "b"), (self.dmp.DIFF_INSERT, "x"), (self.dmp.DIFF_EQUAL, "c"), (self.dmp.DIFF_DELETE, "y"), (self.dmp.DIFF_INSERT, "xabc")], self.dmp.diff_main("abcy", "xaxcxabc", False))
    self.dmp.Diff_DualThreshold = 32

    # Timeout
    self.dmp.Diff_Timeout = 0.001  # 1ms
    # This test may 'fail' on extremely fast computers.  If so, just increase the text lengths.
    self.assertEquals(None, self.dmp.diff_map("`Twas brillig, and the slithy toves\nDid gyre and gimble in the wabe:\nAll mimsy were the borogoves,\nAnd the mome raths outgrabe.", "I am the very model of a modern major general,\nI've information vegetable, animal, and mineral,\nI know the kings of England, and I quote the fights historical,\nFrom Marathon to Waterloo, in order categorical."))
    self.dmp.Diff_Timeout = 0

    # Test the linemode speedup
    # Must be long to pass the 200 char cutoff.
    a = "1234567890\n1234567890\n1234567890\n1234567890\n1234567890\n1234567890\n1234567890\n1234567890\n1234567890\n1234567890\n1234567890\n1234567890\n1234567890\n"
    b = "abcdefghij\nabcdefghij\nabcdefghij\nabcdefghij\nabcdefghij\nabcdefghij\nabcdefghij\nabcdefghij\nabcdefghij\nabcdefghij\nabcdefghij\nabcdefghij\nabcdefghij\n"
    self.assertEquals(self.dmp.diff_main(a, b, False), self.dmp.diff_main(a, b, True))
    a = "1234567890\n1234567890\n1234567890\n1234567890\n1234567890\n1234567890\n1234567890\n1234567890\n1234567890\n1234567890\n1234567890\n1234567890\n1234567890\n"
    b = "abcdefghij\n1234567890\n1234567890\n1234567890\nabcdefghij\n1234567890\n1234567890\n1234567890\nabcdefghij\n1234567890\n1234567890\n1234567890\nabcdefghij\n"
    texts_linemode = self.diff_rebuildtexts(self.dmp.diff_main(a, b, True))
    texts_textmode = self.diff_rebuildtexts(self.dmp.diff_main(a, b, False))
    self.assertEquals(texts_textmode, texts_linemode)


  # MATCH TEST FUNCTIONS


  def testMatchAlphabet(self):
    # Initialise the bitmasks for Bitap
    self.assertEquals({"a":4, "b":2, "c":1}, self.dmp.match_alphabet("abc"))

    self.assertEquals({"a":37, "b":18, "c":8}, self.dmp.match_alphabet("abcaba"))

  def testMatchBitap(self):
    self.dmp.Match_Balance = 0.5
    self.dmp.Match_Threshold = 0.5
    self.dmp.Match_MinLength = 100
    self.dmp.Match_MaxLength = 1000
    # Exact matches
    self.assertEquals(5, self.dmp.match_bitap("abcdefghijk", "fgh", 5))

    self.assertEquals(5, self.dmp.match_bitap("abcdefghijk", "fgh", 0))

    # Fuzzy matches
    self.assertEquals(4, self.dmp.match_bitap("abcdefghijk", "efxhi", 0))

    self.assertEquals(2, self.dmp.match_bitap("abcdefghijk", "cdefxyhijk", 5))

    self.assertEquals(None, self.dmp.match_bitap("abcdefghijk", "bxy", 1))

    # Overflow
    self.assertEquals(2, self.dmp.match_bitap("123456789xx0", "3456789x0", 2))

    # Threshold test
    self.dmp.Match_Threshold = 0.75
    self.assertEquals(4, self.dmp.match_bitap("abcdefghijk", "efxyhi", 1))

    self.dmp.Match_Threshold = 0.1
    self.assertEquals(1, self.dmp.match_bitap("abcdefghijk", "bcdef", 1))
    self.dmp.Match_Threshold = 0.5

    # Multiple select
    self.assertEquals(0, self.dmp.match_bitap("abcdexyzabcde", "abccde", 3))

    self.assertEquals(8, self.dmp.match_bitap("abcdexyzabcde", "abccde", 5))

    # Balance test
    self.dmp.Match_Balance = 0.6  # Strict location, loose accuracy.
    self.assertEquals(None, self.dmp.match_bitap("abcdefghijklmnopqrstuvwxyz", "abcdefg", 24))

    self.assertEquals(0, self.dmp.match_bitap("abcdefghijklmnopqrstuvwxyz", "abcxdxexfgh", 1))

    self.dmp.Match_Balance = 0.4  # Strict accuracy, loose location.
    self.assertEquals(0, self.dmp.match_bitap("abcdefghijklmnopqrstuvwxyz", "abcdefg", 24))

    self.assertEquals(None, self.dmp.match_bitap("abcdefghijklmnopqrstuvwxyz", "abcxdxexfgh", 1))
    self.dmp.Match_Balance = 0.5

  def testMatchMain(self):
    # Full match
    # Shortcut matches
    self.assertEquals(0, self.dmp.match_main("abcdef", "abcdef", 1000))

    self.assertEquals(None, self.dmp.match_main("", "abcdef", 1))

    self.assertEquals(3, self.dmp.match_main("abcdef", "", 3))

    self.assertEquals(3, self.dmp.match_main("abcdef", "de", 3))

    # Complex match
    self.dmp.Match_Threshold = 0.7
    self.assertEquals(4, self.dmp.match_main("I am the very model of a modern major general.", " that berry ", 5))
    self.dmp.Match_Threshold = 0.5


  # PATCH TEST FUNCTIONS


  def testPatchObj(self):
    # Patch Object
    p = dmp_module.patch_obj()
    p.start1 = 20
    p.start2 = 21
    p.length1 = 18
    p.length2 = 17
    p.diffs = [(self.dmp.DIFF_EQUAL, "jump"), (self.dmp.DIFF_DELETE, "s"), (self.dmp.DIFF_INSERT, "ed"), (self.dmp.DIFF_EQUAL, " over "), (self.dmp.DIFF_DELETE, "the"), (self.dmp.DIFF_INSERT, "a"), (self.dmp.DIFF_EQUAL, "\nlaz")]
    strp = str(p)
    self.assertEquals("@@ -21,18 +22,17 @@\n jump\n-s\n+ed\n  over \n-the\n+a\n %0Alaz\n", strp)

  def testPatchFromText(self):
    self.assertEquals([], self.dmp.patch_fromText(""))

    strp = "@@ -21,18 +22,17 @@\n jump\n-s\n+ed\n  over \n-the\n+a\n %0Alaz\n"
    self.assertEquals(strp, str(self.dmp.patch_fromText(strp)[0]))

    self.assertEquals("@@ -1 +1 @@\n-a\n+b\n", str(self.dmp.patch_fromText("@@ -1 +1 @@\n-a\n+b\n")[0]))

    self.assertEquals("@@ -1,3 +0,0 @@\n-abc\n", str(self.dmp.patch_fromText("@@ -1,3 +0,0 @@\n-abc\n")[0]))

    self.assertEquals("@@ -0,0 +1,3 @@\n+abc\n", str(self.dmp.patch_fromText("@@ -0,0 +1,3 @@\n+abc\n")[0]))

    # Generates error
    try:
      self.assertEquals(ValueError, self.dmp.patch_fromText("Bad\nPatch\n"))
    except ValueError:
      self.assertTrue(True)

  def testPatchToText(self):
    strp = "@@ -21,18 +22,17 @@\n jump\n-s\n+ed\n  over \n-the\n+a\n  laz\n"
    p = self.dmp.patch_fromText(strp)
    self.assertEquals(strp, self.dmp.patch_toText(p))

    strp = "@@ -1,9 +1,9 @@\n-f\n+F\n oo+fooba\n@@ -7,9 +7,9 @@\n obar\n-,\n+.\n tes\n"
    p = self.dmp.patch_fromText(strp)
    self.assertEquals(strp, self.dmp.patch_toText(p))

  def testPatchAddContext(self):
    self.dmp.Patch_Margin = 4
    p = self.dmp.patch_fromText("@@ -21,4 +21,10 @@\n-jump\n+somersault\n")[0]
    self.dmp.patch_addContext(p, "The quick brown fox jumps over the lazy dog.")
    self.assertEquals("@@ -17,12 +17,18 @@\n fox \n-jump\n+somersault\n s ov\n", str(p))

    # Same, but not enough trailing context.
    p = self.dmp.patch_fromText("@@ -21,4 +21,10 @@\n-jump\n+somersault\n")[0]
    self.dmp.patch_addContext(p, "The quick brown fox jumps.")
    self.assertEquals("@@ -17,10 +17,16 @@\n fox \n-jump\n+somersault\n s.\n", str(p))

    # Same, but not enough leading context.
    p = self.dmp.patch_fromText("@@ -3 +3,2 @@\n-e\n+at\n")[0]
    self.dmp.patch_addContext(p, "The quick brown fox jumps.")
    self.assertEquals("@@ -1,7 +1,8 @@\n Th\n-e\n+at\n  qui\n", str(p))

    # Same, but with ambiguity.
    p = self.dmp.patch_fromText("@@ -3 +3,2 @@\n-e\n+at\n")[0]
    self.dmp.patch_addContext(p, "The quick brown fox jumps.  The quick brown fox crashes.")
    self.assertEquals("@@ -1,27 +1,28 @@\n Th\n-e\n+at\n  quick brown fox jumps. \n", str(p))

  def testPatchMake(self):
    text1 = "The quick brown fox jumps over the lazy dog."
    text2 = "That quick brown fox jumped over a lazy dog."
    diffs = self.dmp.diff_main(text1, text2, False)
    expectedPatch = "@@ -1,11 +1,12 @@\n Th\n-e\n+at\n  quick b\n@@ -21,18 +22,17 @@\n jump\n-s\n+ed\n  over \n-the\n+a\n  laz\n"
    # Text1+Text2 inputs.
    patches = self.dmp.patch_make(text1, text2)
    self.assertEquals(expectedPatch, self.dmp.patch_toText(patches))

    # Diff input.
    patches = self.dmp.patch_make(diffs)
    self.assertEquals(expectedPatch, self.dmp.patch_toText(patches))

    # Text1+Diff inputs.
    patches = self.dmp.patch_make(text1, diffs)
    self.assertEquals(expectedPatch, self.dmp.patch_toText(patches))

    # Text1+Text2+Diff inputs (deprecated).
    patches = self.dmp.patch_make(text1, text2, diffs)
    self.assertEquals(expectedPatch, self.dmp.patch_toText(patches))

    # Character encoding.
    patches = self.dmp.patch_make("`1234567890-=[]\\;',./", "~!@#$%^&*()_+{}|:\"<>?")
    self.assertEquals("@@ -1,21 +1,21 @@\n-%601234567890-=%5B%5D%5C;',./\n+~!@#$%25%5E&*()_+%7B%7D%7C:%22%3C%3E?\n", self.dmp.patch_toText(patches))

    # Character decoding.
    diffs = [(self.dmp.DIFF_DELETE, "`1234567890-=[]\\;',./"), (self.dmp.DIFF_INSERT, "~!@#$%^&*()_+{}|:\"<>?")]
    self.assertEquals(diffs, self.dmp.patch_fromText("@@ -1,21 +1,21 @@\n-%601234567890-=%5B%5D%5C;',./\n+~!@#$%25%5E&*()_+%7B%7D%7C:%22%3C%3E?\n")[0].diffs)

  def testPatchSplitMax(self):
    # Python's really got no need for this function, but other languages do.
    self.dmp.Match_MaxBits = 32
    patches = self.dmp.patch_make("abcdef1234567890123456789012345678901234567890123456789012345678901234567890uvwxyz", "abcdefuvwxyz")
    self.dmp.patch_splitMax(patches)
    self.assertEquals("@@ -3,32 +3,8 @@\n cdef\n-123456789012345678901234\n 5678\n@@ -27,32 +3,8 @@\n cdef\n-567890123456789012345678\n 9012\n@@ -51,30 +3,8 @@\n cdef\n-9012345678901234567890\n uvwx\n", self.dmp.patch_toText(patches))

    patches = self.dmp.patch_make("1234567890123456789012345678901234567890123456789012345678901234567890", "abc")
    self.dmp.patch_splitMax(patches)
    self.assertEquals("@@ -1,32 +1,4 @@\n-1234567890123456789012345678\n 9012\n@@ -29,32 +1,4 @@\n-9012345678901234567890123456\n 7890\n@@ -57,14 +1,3 @@\n-78901234567890\n+abc\n", self.dmp.patch_toText(patches))

    patches = self.dmp.patch_make("abcdefghij , h : 0 , t : 1 abcdefghij , h : 0 , t : 1 abcdefghij , h : 0 , t : 1", "abcdefghij , h : 1 , t : 1 abcdefghij , h : 1 , t : 1 abcdefghij , h : 0 , t : 1")
    self.dmp.patch_splitMax(patches)
    self.assertEquals("@@ -2,32 +2,32 @@\n bcdefghij , h : \n-0\n+1\n  , t : 1 abcdef\n@@ -29,32 +29,32 @@\n bcdefghij , h : \n-0\n+1\n  , t : 1 abcdef\n", self.dmp.patch_toText(patches))
    self.dmp.Match_MaxBits = 0

  def testPatchAddPadding(self):
    # Both edges full
    patches = self.dmp.patch_make("", "test")
    self.assertEquals("@@ -0,0 +1,4 @@\n+test\n", self.dmp.patch_toText(patches))
    self.dmp.patch_addPadding(patches)
    self.assertEquals("@@ -1,8 +1,12 @@\n %00%01%02%03\n+test\n %00%01%02%03\n", self.dmp.patch_toText(patches))

    # Both edges partial
    patches = self.dmp.patch_make("XY", "XtestY")
    self.assertEquals("@@ -1,2 +1,6 @@\n X\n+test\n Y\n", self.dmp.patch_toText(patches))
    self.dmp.patch_addPadding(patches)
    self.assertEquals("@@ -2,8 +2,12 @@\n %01%02%03X\n+test\n Y%00%01%02\n", self.dmp.patch_toText(patches))

    # Both edges none
    patches = self.dmp.patch_make("XXXXYYYY", "XXXXtestYYYY")
    self.assertEquals("@@ -1,8 +1,12 @@\n XXXX\n+test\n YYYY\n", self.dmp.patch_toText(patches))
    self.dmp.patch_addPadding(patches)
    self.assertEquals("@@ -5,8 +5,12 @@\n XXXX\n+test\n YYYY\n", self.dmp.patch_toText(patches))

  def testPatchApply(self):
    # Exact match
    patches = self.dmp.patch_make("The quick brown fox jumps over the lazy dog.", "That quick brown fox jumped over a lazy dog.")
    results = self.dmp.patch_apply(patches, "The quick brown fox jumps over the lazy dog.")
    self.assertEquals(("That quick brown fox jumped over a lazy dog.", [True, True]), results)

    # Partial match
    results = self.dmp.patch_apply(patches, "The quick red rabbit jumps over the tired tiger.")
    self.assertEquals(("That quick red rabbit jumped over a tired tiger.", [True, True]), results)

    # Failed match
    results = self.dmp.patch_apply(patches, "I am the very model of a modern major general.")
    self.assertEquals(("I am the very model of a modern major general.", [False, False]), results)

    # No side effects
    patches = self.dmp.patch_make("", "test")
    patchstr = self.dmp.patch_toText(patches)
    results = self.dmp.patch_apply(patches, "")
    self.assertEquals(patchstr, self.dmp.patch_toText(patches))

    # No side effects with major delete
    patches = self.dmp.patch_make("The quick brown fox jumps over the lazy dog.", "Woof")
    patchstr = self.dmp.patch_toText(patches)
    self.dmp.patch_apply(patches, "The quick brown fox jumps over the lazy dog.")
    self.assertEquals(patchstr, self.dmp.patch_toText(patches))

    # Edge exact match
    patches = self.dmp.patch_make("", "test")
    self.dmp.patch_apply(patches, "")
    self.assertEquals(("test", [True]), results)

    # Near edge exact match
    patches = self.dmp.patch_make("XY", "XtestY")
    results = self.dmp.patch_apply(patches, "XY")
    self.assertEquals(("XtestY", [True]), results)

    # Edge partial match
    patches = self.dmp.patch_make("y", "y123")
    results = self.dmp.patch_apply(patches, "x")
    self.assertEquals(("x123", [True]), results)


if __name__ == "__main__":
  unittest.main()
