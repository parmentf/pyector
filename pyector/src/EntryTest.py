#!/usr/bin/env python
# coding: utf-8

# pyECTOR, learning chatterbot, by François PARMENTIER
# http://code.google.com/p/pyector/
# Copyright (C) 2008 François PARMENTIER
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

# François PARMENTIER - parmentierf@users.sourceforge.net

# $Id$
"""Unit test for Entry.py
"""

__author__    = "François Parmentier (parmentierf@users.sourceforge.net)"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2008 François Parmentier"
__license__   = "GPL"

from Entry import *
import unittest


class EntryTest(unittest.TestCase):
    "Test the Entry class"
    def testSentencesOne(self):
        "Separate only one sentence"
        e    = Entry("One.")
        self.assertEqual(["One."], e.getSentences())

    def testSentenceWithoutPunctuation(self):
        "Separate one sentence without punctuation"
        e    = Entry("One")
        self.assertEqual(["One"], e.getSentences())

    def testSentenceEndPunctations(self):
        "Separate one sentence with several end punctuation characters"
        line     = "One..."
        e        = Entry(line)
        self.assertEqual([line], e.getSentences())

    def testSentenceTwo(self):
        "Separate two sentences"
        e    = Entry("One. Two!")
        self.assertEqual(["One.","Two!"], e.getSentences())


if __name__ == "__main__":
    unittest.main()
