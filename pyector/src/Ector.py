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
import os


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

    def getTypeName(self):
        return self.__type

    def getDecay(self):
        return self.__decay

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


class SentenceNode(Node):
    """A sentence node.

    TODO: use attributes to store how many times the sentence is at the
          beginning of a dialogue or (more difficult) at the end of one.
          Better: use attributes to store how many times the sentence
          is the first phrase, the last one, or a middle one in the line.
    """
    __type = "sentence"
    __decay = 50
    def __init__(self, symbol, occ = 1):
        Node.__init__(self, symbol, occ=occ)

    def getTypeName(self):
        return self.__type

    def getDecay(self):
        return self.__decay


class ExpressionNode(Node):
    """An expression node.

    An expression is a sequence of several tokens.
    """
    __type = "expression"
    __decay = 40
    def __init__(self, symbol, occ = 1):
        Node.__init__(self, symbol, occ=occ)

    def getTypeName(self):
        return self.__type

    def getDecay(self):
        return self.__decay


class SentimentNode(Node):
    """A sentiment node.
    """
    __type = "sentiment"
    __decay = 10
    def __init__(self, symbol, occ = 1):
        Node.__init__(self, symbol, occ=occ)

    def getTypeName(self):
        return self.__type

    def getDecay(self):
        return self.__decay


class UttererNode(Node):
    """An utterer node.

    An utterer say sentences.
    """
    __type = "utterer"
    __decay = 70
    def __init__(self, symbol, occ = 1):
        Node.__init__(self, symbol, occ=occ)

    def getTypeName(self):
        return self.__type

    def getDecay(self):
        return self.__decay


class Ector:
    "The ECTOR class"
    def __init__(self,botname="Ector",username="User"):
        self.botname  = botname
        self.username = username
        if os.path.exists("cn.pkl"):
            f    = open("cn.pkl","r")
            self.cn    = pickle.load(f)
            f.close()
        else:
            self.cn    = ConceptNetwork()
        self.loadUserState()

    def dump(self):
        """Save ECTOR.

        Save the ConceptNetwork in cn.pkl, and the state in usernameState.pkl"""
        # Save the ConceptNetwork
        f = open("cn.pkl","w")
        self.cn.dump(f)
        f.close()
        # Save username's state
        if self.username:
            filename = self.__getStateId()
            f        = open(filename,"w")
            state    = self.cn.getState(username)
            pickle.dump(state,f,2)
            f.close()

    def showStatus(self):
        """Show Ector's status (ConceptNetwork stats, states)"""
        self.cn.showNodes()
        self.cn.showStates()

    def __getStateId(self):
        """Create a state id from the username"""
        return self.username + "_state.pkl"

    def setUser(self,username):
        """Change user's name.

        Create a new state, if it does not exist.
        """
        self.username    = username
        try:
            self.cn.getState(username)
        except:
            self.loadUserState()

    def loadUserState(self):
        """Load the state matching username"""
        if self.username:
            filename    = self.__getStateId()
            if os.path.exists(filename):
                f           = open(filename,"r")
                state       = pickle.load(f)
                f.close()
            else:
                state    = State(self.username)
            self.cn.addState(state)


def main():
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
#    print "Args    = %s" % args
#    print "Options = %s" % options
#    print "botname = %s" % options.botname.capitalize()
#    print "verbose = %s" % options.verbose

    license  = None
    stdin    = sys.stdin
    stdout   = sys.stdout
    username = options.username and options.username or ""
    botname  = options.botname.capitalize()
    version  = "0.2"

    ector    = Ector(botname, username)

    print """pyECTOR version %s, Copyright (C) 2008 Francois PARMENTIER
pyECTOR comes with ABSOLUTELY NO WARRANTY; for details type `@show w'.
This is free software, and you are welcome to redistribute it
under certain conditions; type `@show c' for details.
@help gives a basic help on pyECTOR commands.""" % (version)

    while True:
        if stdin.closed:
            break
        stdout.write(username+">")
        entry = stdin.readline().strip()

        # No Warranty
        if entry[:7] == "@show w":
            if not license:
                f = open("../LICENSE")
                license = f.readlines()
                f.close()
            for i in range(257,278):
                stdout.write(license[i])
        # Conditions
        elif entry[:7] == "@show c":
            if not license:
                f = open("../LICENSE")
                license = f.readlines()
                f.close()
            for i in range(57,256):
                stdout.write(license[i])
        elif entry[:6] == "@usage":
            print usage.replace("%prog", "Ectory.py")
        elif entry[:7] == "@status":
            ector.showStatus()
        elif entry[:8] == "@person ":
            username = entry[8:].strip()
            ector.setUser(username)
        elif entry[:6] == "@name ":
            botname = entry[6:].strip()
            ector.setName(botname)
        elif entry[:8] == "@version":
            print "Version: %s" % (version)
        elif entry[:6] == "@write":
            ector.dump()
        elif entry[:5] == "@quit" or entry[:5] == "@exit" or entry[:4] == "@bye":
            return 0
        # Help
        elif entry[:5] == "@help":
            print """ - @usage   : print the options of the Ector.py command
 - @quit    : quit
 - @exit    : quit
 - @bye     : quit
 - @person  : change the utterer name (like -p)
 - @name    : change the bot's name (like -n)
 - @version : give the current version
 - @write   : save Ector's Concept Network and state
 - @status  : show the status of Ector (Concept Network, states)"""

if __name__ == "__main__":
    import sys
    status = main()
    sys.exit(status)
