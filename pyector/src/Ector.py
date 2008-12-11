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

# See http://pyector.googlecode.com/
# $Id$

__author__    = "François Parmentier (parmentierf@users.sourceforge.net)"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2008 François Parmentier"
__license__   = "GPL"

from ConceptNetwork import *
from Entry          import Entry
from time           import localtime
import os
import sys, locale

ENCODING    = locale.getdefaultlocale()[1]
DEFAULT_ENCODING    = sys.getdefaultencoding()

class TokenNode(Node):
    """A token in a sentence.

    That should be a word, a smiley, or punctuation sign(s).

    This TokenNode remembers:
    beg    :    occurrence in the beginning of a sentence
    mid    :    occurrence in the middle of a sentence
    end    :    occurrence in the end of a sentence
    """
    __type = "token"
    __decay = 20    # 40
    def __init__(self, symbol, occ = 1, beg = 0, mid = 0, end = 0):
        self.__beg = beg
        self.__mid = mid
        self.__end = end
        Node.__init__(self, symbol, occ=occ)

    def addNode(self,node):
        """Add beg, mid, and end of the node to self."""
        Node.addNode(self, node)
        self.__beg += node.getBeginningOccurrence()
        self.__mid += node.getMiddleOccurrence()
        self.__end += node.getEndOccurrence()

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

    def show(self):
        """Display the node"""
        print "%10s (%8s): %d (%d,%d,%d)" % (self.getSymbol().encode(ENCODING),
                               self.getTypeName(),
                               self.getOcc(),
                               self.getBeginningOccurrence(),
                               self.getMiddleOccurrence(),
                               self.getEndOccurrence())



class SentenceNode(Node):
    """A sentence node.

    - beg: number of occurrences of this sentence in top of the dialogue.
    """
    __type = "sentence"
    __decay = 25    # 50
    def __init__(self, symbol, occ = 1):
        Node.__init__(self, symbol, occ=occ)
        self.beg    = 0

    def addNode(self,node):
        """Add beg, mid, and end of the node to self."""
        Node.addNode(self, node)
        self.beg += node.beg

    def getTypeName(self):
        return self.__type

    def getDecay(self):
        return self.__decay

    def show(self):
        """Display the node
        Display the number of times it was on top of a dialogue."""
        print "%10s (%8s): %d (%d)" % (self.getSymbol().encode(ENCODING),
                               self.getTypeName(),
                               self.getOcc(),
                               self.beg
                               )


class ExpressionNode(Node):
    """An expression node.

    An expression is a sequence of several tokens.
    """
    __type = "expression"
    __decay = 20    # 40
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
    __decay = 5    # 10
    def __init__(self, symbol, occ = 1):
        Node.__init__(self, symbol, occ=occ)

    def getTypeName(self):
        return self.__type

    def getDecay(self):
        return self.__decay


class UttererNode(Node):
    """An utterer node.

    An utterer say sentences.
    The last time he uttered is reminded.
    """
    __type = "utterer"
    __decay = 35    # 70
    __lastTime = None
    def __init__(self, symbol, occ = 1):
        Node.__init__(self, symbol, occ=occ)
        self.__lastTime    = time.localtime()

    def getTypeName(self):
        return self.__type

    def getDecay(self):
        return self.__decay

    def getLastTime(self):
        """Get the last time the utterer talked"""
        return self.__lastTime

    def addNode(self,node):
        """Update the last time the utterer talked."""
        Node.addNode(self, node)
        self.__lastTime = time.localtime()

    def show(self):
        """Display the node
        Display the last time the utterer talked"""
        print "%10s (%8s): %d (%d/%d/%d)" % (self.getSymbol(),
                               self.getTypeName(),
                               self.getOcc(),
                               self.__lastTime[0],
                               self.__lastTime[1],
                               self.__lastTime[2]
                               )

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
            state    = self.cn.getState(self.username)
            pickle.dump(state,f)
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

    def addEntry(self,entry):
        """Add an entry into the Concept Network of Ector.

        Add an entry into the Concept Network of Ector.
        An entry may be constituted from several sentences.
        When file is not NULL, it is taken instead utterer.

        - entry     entry to add

        Return the last sentenceNode of the entry.
        """
        state               = self.cn.getState(self.username)
        e = Entry(entry, self.username, self.botname)
        sentences           = e.getSentences()
        lastSentenceNode    = None
        for sentence in sentences:
            sentenceNode = self.addSentence(sentence)
            state.fullyActivate(sentence, "sentence")
            if lastSentenceNode:
                self.cn.addLink(lastSentenceNode,sentenceNode)
            lastSentenceNode = sentenceNode
        return lastSentenceNode

    def addSentence(self,sentence):
        """Add a sentence into the Concept Network of Ector.

        Add a sentence into the Concept Network of Ector.
        Adds its tokens too.

        /*
        except when
        the sentence already exists (in this case, the occurrence is not
        incremented, nor are expression created -this should lead to the
        creation of expressions identical to the sentence).
        */

        In the case where file exist, username is not
        taken into account, but file is, and is of type "file".

        -  sentence   sentence to add

        Return   the node of the sentence added."""
        state          = self.cn.getState(self.username)
        # Activate the utterer, and add it to the concept network
        uttererNode    = UttererNode(self.username)
        self.cn.addNode(uttererNode)
        state.fullyActivate(self.username, "utterer")
        # Add the sentence node to the concept network.
        sentenceNode   = SentenceNode(sentence)
        self.cn.addNode(sentenceNode)
        #state.setNodeActivationValue(100, sentence, "sentence")
        state.fullyActivate(sentence, "sentence")
        # TODO: if the occurrence of the sentence node is only 1,
        #       compute the expressions
        pass
        # Link it to the utterer node.
        self.cn.addBidirectionalLink(uttererNode, sentenceNode)
        # Add the tokens to the concept network, link them to the sentence
        e                 = Entry("None")
        tokens            = e.getTokens(sentence)
        beginning         = 1
        middle            = 0
        end               = 0
        previousTokenNode = None
        i                 = 0
        for token in tokens:
            i += 1
            if i == len(tokens):
                end    = 1
            # Add the token node to the concept network
            tokenNode = TokenNode(token, 1, beginning, middle, end)
            self.cn.addNode(tokenNode)
            state.fullyActivate(token, "token")
            if beginning:
                beginning = 0
                middle    = 1
            if middle and i == len(tokens) - 1:
                middle    = 0
                end       = 1
            # Link it to the previous node
            if previousTokenNode:
                self.cn.addLink(previousTokenNode,tokenNode)
            previousTokenNode = tokenNode
            # Link it to the sentence node
            self.cn.addBidirectionalLink(tokenNode, sentenceNode)
        return sentenceNode

    def propagate(self,times=1):
        """Propagate the activation in the state of the utterer"""
        state = self.cn.getState(self.username)
        for i in range(times):
            self.cn.fastPropagateActivations(state)

    def getActivatedSentenceNode(self):
        """Get one of the most activated sentences"""
        state        = self.cn.getState(self.username)
        maximumAV    = state.getMaximumActivationValue(self.cn, "sentence")
        sentences    = state.getActivatedTypedNodes(self.cn, "sentence",
                                                    maximumAV - 10)
        # TODO: compute a temperature according the state's activations
        temperature  = Temperature(60)
        if sentences:
            sentenceNode = temperature.chooseWeightedItem(sentences)
            return sentenceNode
        else:
            return ''

    def showState(self, stateID):
        """Show the state matching stateID"""
        state        = self.cn.getState(stateID)
        state.showNodes()

    def showLinks(self, stateId=None):
        """Show the links of the concept network, using stateID"""
        if stateId == None:
            stateId = self.username
        state    = self.cn.getState(stateId)
        self.cn.showLinks(stateId)

    def generateForward(self, phrase, temperature):
        """Generate the end of a sentence, adding tokens to the list
        of token nodes in phrase."""
        state     = self.cn.getState(self.username)
        outgoingLinks    = phrase[-1].outgoingLinks
        nextNodes    = []
        for link in outgoingLinks:
            toNode    = link.getNodeTo()
            if toNode.getTypeName() == "token":
                av    = state.getNodeActivationValue(toNode.getSymbol(), "token")
                if av == 0:
                    av = 1
                nbRepet    = phrase.count(toNode)
                length     = len(toNode.getSymbol())
                # If the node is not present more than 3 times
                if nbRepet * length <= 5 * 3:
                    repetition    = 1 + nbRepet * nbRepet * length
                    nextNodes    += [(toNode, link.getCoOcc() * av / repetition)]
        # Stop condition
        if len(nextNodes) == 0:
            return phrase
        # Choose one node among the tokens following the one at the end
        # of the phrase
        chosenToken    = temperature.chooseWeightedItem(nextNodes)
        phrase        += [chosenToken]

        return self.generateForward(phrase, temperature)

    def generateBackward(self, phrase, temperature):
        """Generate the beginning of a sentence, adding tokens to the list
        of token nodes in phrase."""
        state     = self.cn.getState(self.username)
        incomingLinks    = phrase[0].incomingLinks
#        previousNodes    = [(link.getNodeFrom(), link.getCoOc())
#                            for link in incomingLinks
#                            if link.getNodeFrom().getTypeName() == "token"]
        previousNodes    = []
        for link in incomingLinks:
            fromNode    = link.getNodeFrom()
            if fromNode.getTypeName() == "token":
                av    = state.getNodeActivationValue(fromNode.getSymbol(), "token")
                if av == 0:
                    av = 1
                nbRepet    = phrase.count(fromNode)
                length     = len(fromNode.getSymbol())
                # If the node is not present more than 3 times
                if nbRepet * length <= 5 * 3:
                    repetition    = 1 + nbRepet * nbRepet * length
                    previousNodes    += [(link.getNodeFrom(), link.getCoOcc() * av)]
        # Stop condition
        if len(previousNodes) == 0:
            return phrase
        # Choose one node among the tokens preceding the one at the beginning
        # of the phrase
        chosenToken   = temperature.chooseWeightedItem(previousNodes)
        phrase        = [chosenToken] + phrase

        return self.generateBackward(phrase, temperature)

    def generateSentence(self, debug=False):
        """Get one node, generate a sentence from it forwards to the end
        of the sentence, and then generate backwards to the beginning of
        the sentence.

        Return a tuple containing the generated sentence as a string and
        the nodes of the sentence."""
        # Choose a token node among the most activated
        state     = self.cn.getState(self.username)
        maximumAV = state.getMaximumActivationValue(self.cn, "token")
        tokens    = state.getActivatedTypedNodes(self.cn,"token",
                                                 maximumAV - 10)
        # TODO: compute a temperature according the state's activations
        temperature    = Temperature(60)
        chosenToken    = temperature.chooseWeightedItem(tokens)

        phrase    = [chosenToken]
        # Generate forwards
        phrase    = self.generateForward(phrase, temperature)
        # Generate backwards
        phrase    = self.generateBackward(phrase, temperature)
        strPhrase = [token.getSymbol() for token in phrase]
        if debug:
            return (("_".join(strPhrase)) + " (%s)" % chosenToken.getSymbol(),
                    phrase)
        else:
            return (self.beautifySentence(" ".join(strPhrase)),
                    phrase)

    def beautifySentence(self, sentence):
        """Beautify a string, which is a generated sentence, where
        tokens (words and punctuation) are separated by spaces.

        No need to get a space between a word and a comma."""
        sentence    = sentence.replace(" , ",    ", ")
        sentence    = sentence.replace(" .",     ".")
        sentence    = sentence.replace(" : ",    ": ")
        sentence    = sentence.replace(" !",     "!")
        sentence    = sentence.replace(" ?",     "?")
        sentence    = sentence.replace(" ' ",    "'")
        sentence    = sentence.replace(" ( ",    " (")
        sentence    = sentence.replace(" )",     ")")
        sentence    = sentence.replace(" - ",    "-")
        return sentence

    def cleanState(self):
        """Clean the not activated nodes states in the state"""
        state     = self.cn.getState(self.username)
        state.clean()


def logEntry(filename, utterer, entry, encoding=ENCODING):
    """Log the utterer's entry in the file"""
    f    = file(filename,"a")
    t    = time.localtime()
    print >> f, "%4d/%2d/%2d - %2d:%2d:%2d\t%s\t%s" % (t[0], t[1], t[2],
                                                   t[3], t[4], t[5],
                                                   utterer,
                                                   entry.encode(encoding))
    f.close()


def main():
    # Each decay divided by 2
    UttererNode.__decay    = 5
    SentimentNode.__decay  = 5
    ExpressionNode.__decay = 20
    SentenceNode.__decay   = 25
    TokenNode.__decay      = 20
    from optparse import OptionParser

    usage="usage: %prog [-p username][-n botname=Ector][-v|-q][-l logfilepath=ector.log][-s|-g][-h]"
    parser = OptionParser(usage=usage,version="%prog 0.3")
    parser.add_option("-p", "--person", dest="username", default="User",
                      help="set the name of the utterer")
    parser.add_option("-n", "--name", dest="botname", default="Ector",
                      help="set the name of the bot")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=True,
                      help="say all that you can say")
    parser.add_option("-q", "--quiet", action="store_false", dest="verbose",
                      help="shut up!")
    parser.add_option("-l", "--log", dest="logname", default="ector.log",
                      help="log the dialogue in log file")
    parser.add_option("-s", "--sentence", action="store_true", dest="sentence", default=False,
                      help="set sentence reply mode on")
    parser.add_option("-g", "--generate", action="store_false", dest="sentence",
                      help="set generate reply mode on")
    parser.add_option("-d", "--debug", action="store_true", dest="debug", default=False,
                      help="set debug mode on")

    (options, args) = parser.parse_args()

    license  = None
    stdin    = sys.stdin
    stdout   = sys.stdout
    username = options.username
    botname  = options.botname.capitalize()
    logfilename = options.logname
    version  = "0.4"
    sentence_mode = options.sentence
    generate_mode = not sentence_mode    # sentence and generate modes are antagonist
    verbose  = options.verbose
    debug    = options.debug

    # Quiet mode is above sentence or generate modes
    if not verbose:
        sentence_mode    = False
        generate_mode    = False

    ector    = Ector(botname, username)

    previousSentenceNode    = None
    nodes                   = None

    print """pyECTOR version %s, Copyright (C) 2008 Francois PARMENTIER
pyECTOR comes with ABSOLUTELY NO WARRANTY; for details type `@show w'.
This is free software, and you are welcome to redistribute it
under certain conditions; type `@show c' for details.
@help gives a basic help on pyECTOR commands.""" % (version)

    ector_path    = os.path.dirname(sys.argv[0])
    license_path  = os.path.abspath(ector_path + "/../LICENSE")

    while True:
        if stdin.closed:
            break
        stdout.write(username+">")
        entry = stdin.readline().strip()

        # No Warranty
        if entry[:7] == "@show w":
            if not license:
                f = open(license_path)
                license = f.readlines()
                f.close()
            for i in range(257,278):
                stdout.write(license[i])
        # Conditions
        elif entry[:7] == "@show c":
            if not license:
                f = open(license_path)
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
            print "pyECTOR version %s" % (version)
        elif entry[:6] == "@write":
            ector.dump()
        elif entry[:5] == "@quit" or entry[:5] == "@exit" or entry[:4] == "@bye":
            return 0
        elif entry[:10] == "@shownodes":
            ector.cn.showNodes()
        elif entry[:10] == "@showlinks":
            ector.showLinks()
        elif entry == "@showstate":
            ector.showState(username)
        elif entry == "@cleanstate":
            ector.cleanState()
        elif entry.startswith("@log "):
            logfilename    = entry[5:]
            print "Log file: %s" % (logfilename)
        elif entry == "@log" or entry == "@logoff":
            print "Log off (%s)" % logfilename
            logfilename = ''
        elif entry.lower() == "@sentence on":
            sentence_mode = True
            generate_mode = False     # sentence and generate modes are not compatible
            print "Sentence reply mode ON"
        elif entry.lower() == "@sentence off":
            sentence_mode = False
            print "Sentence reply mode OFF"
        elif entry.lower() == "@sentence":
            print "Sentence reply mode", sentence_mode and "ON" or "OFF"
        elif entry.lower() == "@generate on":
            sentence_mode = False
            generate_mode = True     # sentence and generate modes are not compatible
            print "Generate reply mode ON"
        elif entry.lower() == "@generate off":
            generate_mode = False
            print "Sentence reply mode OFF"
        elif entry.lower() == "@generate":
            print "Generate reply mode", generate_mode and "ON" or "OFF"
        elif entry.lower() == "@debug on":
            debug    = True
            print "Debug mode ON"
        elif entry.lower() == "@debug off":
            debug    = False
            print "Debug mode OFF"
        elif entry.lower() == "@debug":
            print "Debug mode", debug and "ON" or "OFF"
        # Help
        elif entry[:5] == "@help":
            print """You can just start typing phrases.
But there are some commands you can use:
 - @usage     : print the options of the Ector.py command
 - @quit      : quit
 - @exit      : quit
 - @bye       : quit
 - @person    : change the utterer name (like -p)
 - @name      : change the bot's name (like -n)
 - @version   : give the current version
 - @write     : save Ector's Concept Network and state
 - @shownodes : show the nodes of the Concept Network
 - @showlinks : show the links of the Concept Network
 - @showstate : show the state of the nodes
 - @cleanstate: clean the state from the non-activated nodes
 - @log [file]: log the entries in the file (no file turns off the logging)
 - @status    : show the status of Ector (Concept Network, states)
 - @sentence [ON|OFF]: set the sentence reply mode
 - @generate [ON|OFF]: set the generate reply mode
 - @debug [ON|OFF]: set the debug mode on or off"""
        elif entry.startswith("@"):
            print "There is no command",entry
        elif entry:
             entry    = unicode(entry, ENCODING)
             lastSentenceNode = ector.addEntry(entry)
             if previousSentenceNode:
                 ector.cn.addLink(previousSentenceNode,lastSentenceNode)
             elif sentence_mode:
                 # First sentence of a dialogue
                 lastSentenceNode.beg += 1

             if nodes and lastSentenceNode:
                 # Make a link from the nodes of the generated
                 # sentence to the next entry.
                 # BEWARE: may make a link co-occurrence greater than the
                 # sentence node occurrence.
                 for node in nodes:
                     ector.cn.addLink(node, lastSentenceNode)

             previousSentenceNode    = lastSentenceNode
             # if log is activated, log the entry.
             if logfilename:
                 logEntry(logfilename, username, entry)
             # Propagate activation
             ector.cleanState()
             ector.propagate(2)
#             ector.showState(username)
             # Get the reply
             reply    = None
             if sentence_mode:
                 # Get one of the most activated sentences
                 replyNode = ector.getActivatedSentenceNode()
                 reply     = replyNode.getSymbol()
                 reply     = reply.replace("@bot@",  username)
                 reply     = reply.replace("@user@", botname)
                 previousSentenceNode = replyNode
             elif generate_mode:
                 (reply, nodes)    = ector.generateSentence(debug)
                 reply     = reply.replace("@bot@",  username)
                 reply     = reply.replace("@user@", botname)
                 previousSentenceNode = None
             if reply:
                 print "%s>" % (ector.botname), reply.encode(ENCODING)
                 if logfilename:
                     logEntry(logfilename, botname, reply)
        else:
             if debug:
                 print "No entry given."


if __name__ == "__main__":
    import sys
    status = main()
    sys.exit(status)
