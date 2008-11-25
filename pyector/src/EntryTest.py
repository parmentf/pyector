#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
        e    = Entry("One. Two")
        self.assertEqual(["One.","Two"], e.getSentences())

    def testSentenceFour(self):
        "Separate two sentences"
        e    = Entry("One. Two! Three? Four.")
        self.assertEqual(["One.","Two!","Three?","Four."], e.getSentences())

    def testSentenceOneUrl(self):
        "Parse one sentence containing an URL"
        e    = Entry("The site http://pyector.googlecode.com/ is great!")
        self.assertEqual(["The site http://pyector.googlecode.com/ is great!"],
                         e.getSentences())

    def testSentenceOneSmiley(self):
        "Parse one sentence containing a smiley"
        e    = Entry("Eheh :) this is cool")
        self.assertEqual(["Eheh :) this is cool"], e.getSentences())

    def testSentenceOneAcronym(self):
        "Parse one sentence containing acronyms"
        e    = Entry("A.I. means Artificial Intelligence.")
        self.assertEqual(["A.I. means Artificial Intelligence."], e.getSentences())

    def testSentenceOneMail(self):
        "Parse one sentence containing mail"
        line = "The mail of my developer is parmentierf@users.sourceforge.net."
        e    = Entry(line)
        self.assertEqual([line], e.getSentences())

    def testSentenceOneMail2(self):
        "Parse one sentence containing a mail with a dotted name"
        line = "The mail of my developer is foo.bar@users.sourceforge.net."
        e    = Entry(line)
        self.assertEqual([line], e.getSentences())

    def testSentenceOneLines(self):
        """Parse one sentence in several lines.
        Lines have to be appended."""
        lines = """How
are you?"""
        e     = Entry(lines)
        self.assertEqual(["How are you?"], e.getSentences())

    def testSentenceTwoSmiley(self):
        """Parse two sentences: one normal, and one smiley"""
        line     = "What happen with a smiley? :)"
        e        = Entry(line)
        self.assertEqual(["What happen with a smiley?",":)"],e.getSentences())

    def testBotname(self):
        """Replace botname by '@bot@'"""
        e    = Entry("Ector is the director!")
        self.assertEqual("@bot@ is the director!",e.entry)
        self.assertEqual(["@bot@","is","the","director","!"],
                         e.getTokens("@bot@ is the director!"))

    def testUsername(self):
        """Replace user name by '@user@'"""
        e    = Entry("François is the bot master!",username="François")
        self.assertEqual("@user@ is the bot master!",e.entry)
        self.assertEqual(["@user@","is","the","bot","master","!"],
                         e.getTokens("@user@ is the bot master!"))

    def testTokens(self):
        """Get the tokens of one sentence"""
        line = "This sentence is not important."
        e    = Entry(line)
        self.assertEqual(["This","sentence","is","not","important","."],
                         e.getTokens(line))

    def testTokensSmiley(self):
        """Get tokens comprising smileys"""
        line = "This should work :)"
        e    = Entry(line)
        self.assertEqual(["This","should","work",":)"], e.getTokens(line))
        line = "This should work too :)."
        self.assertEqual(["This","should","work","too",":)","."], e.getTokens(line))
        line = ":D"
        self.assertEqual([":D"], e.getTokens(line))

    def testTokensUnicode(self):
        """Get tokens with accented characters"""
        line = u"Comment ça va?"
        e    = Entry(line)
        self.assertEqual([u"Comment",u"ça",u"va",u"?"], e.getTokens(line))


if __name__ == "__main__":
    unittest.main()
