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

# See http://pyector.googlecode.com/
# $Id$

__author__    = "François Parmentier (parmentierf@users.sourceforge.net)"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2008 François Parmentier"
__license__   = "GPL"

from ConceptNetwork import *

class TokenNode(Node):
    """A token in a sentence.

    That should be a word, or punctuation sign(s).

    This TokenNode remembers:
    beg    :    occurrence in the beginning of a sentence
    mid    :    occurrence in the middle of a sentence
    end    :    occurrence in the end of a sentence
    """
    __type = "token"
    __decay = 40
    def __init__(self, symbol, occ = 1, beg = 0, mid = 0, end = 0):
        self.__beg = beg
        self.__mid = mid
        self.__end = end
        Node.__init__(self, symbol, occ=occ)

    def getBeginningOccurrence(self):
        return self.__beg

    def getMiddleOccurrence(self):
        return self.__mid

    def getEndOccurrence(self):
        return self.__end

    def incrementBeginningOccurrence(self):
        self.__beg += 1
        return self.__beg

    def incrementMiddleOccurrence(self):
        self.__mid += 1
        return self.__mid

    def incrementEndOccurrence(self):
        self.__end += 1
        return self.__end

if __name__ == "__main__":
    from optparse import OptionParser
    usage="usage: %prog [-p username][-n botname=Ector][-v|-q][-l logfilepath][-s|-g][-h]"
    parser = OptionParser(usage=usage,version="%prog 0.1")
    parser.add_option("-p", "--person", dest="username",
                      help="give the name of the utterer")
    parser.add_option("-n", "--name", dest="botname", default="Ector",
                      help="give the name of the bot")
    parser.add_option("-v", action="store_true", dest="verbose", default=False,
                      help="say all that you can say")
    parser.add_option("-q", action="store_false", dest="verbose",
                      help="shut up!")

    (options, args) = parser.parse_args()
    print "Args    = %s" % args
    print "Options = %s" % options
    print "botname = %s" % options.botname.capitalize()
    print "verbose = %s" %options.verbose

