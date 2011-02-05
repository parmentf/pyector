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
"""Unit test for Ector.py

Test the Ector class, as much as one can.
"""

__author__    = "François Parmentier (parmentierf@users.sourceforge.net)"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2008 François Parmentier"
__license__   = "GPL"

from Ector import *
import unittest


class EctorTest(unittest.TestCase):
    "Test the Node class"
    def testAddSentence(self):
        """Add a sentence in the Concept Network of Ector"""
        ector    =    Ector()
        ector.addSentence("Hello.")
        expectedNodeSymbols    = ["User", "Hello", ".", "Hello."]
        nodeSymbols    = [symbol for (symbol, typeName) in ector.cn.node]
        self.assertEqual(expectedNodeSymbols,nodeSymbols)

    def testAddEntry(self):
        """Add an entry in Ector"""
        ector    =    Ector()
        ector.addEntry("Hello.")
        expectedNodeSymbols    = ["User", "Hello", ".", "Hello."]
        nodeSymbols    = [symbol for (symbol, typeName) in ector.cn.node]
        self.assertEqual(expectedNodeSymbols,nodeSymbols)

    def testLinksCoOcc(self):
        """When two nodes are linked several times, the nodes' co-occurrence
        has to be incremented"""
        ector    =    Ector()
        ector.addSentence("how do you do?")
        ector.addSentence("do you?")
        doToken  = ector.cn.getNode("do", "token")
        youToken = ector.cn.getNode("you", "token")
        link     = ector.cn.getLink(doToken, youToken)
        self.assertEqual(2, link.getCoOcc())


if __name__ == "__main__":
    unittest.main()

