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
"""Definitions of the Entry class.

An entry is a line of input, which has to be parsed into sentences,
sentences into tokens, and tokens join to expressions.
"""
__author__    = "François Parmentier (parmentierf@users.sourceforge.net)"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2008 François Parmentier"
__license__   = "GPL"

import re

reSENTENCES_SEPARATORS = re.compile(r'[?!\.]+\s*', re.LOCALE|re.UNICODE)
# From http://www.regular-expressions.info/email.html
reMAIL     = re.compile(r"([a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+(?:[A-Z]{2}|com|org|net|gov|mil|biz|info|mobi|name|aero|jobs|museum))",
                          re.IGNORECASE|re.MULTILINE|re.UNICODE)
reACRONYMS = re.compile(r'(?:[A-Z]\.)+', re.LOCALE|re.UNICODE)
reURL      = re.compile(r"(?:http|ftp|file)://(?:[a-z0-9]+\.){1,3}[a-z0-9]+", re.IGNORECASE|re.UNICODE)
#reURL      = re.compile(r"([^:/?#]+:)?(?://[^/?#]*)?[^?#]*(?:\?[^#]*)?(?:#.*)?", re.IGNORECASE)

#r"(([a-zA-Z][0-9a-zA-Z+\\-\\.]*:)?/{0,2}[0-9a-zA-Z;/?:@&=+$\\.\\-_!~*'()%]+)?(#[0-9a-zA-Z;/?:@&=+$\\.\\-_!~*'()%]+)?"
#r"(?:http|ftp|file)://(?:[a-z0-9]+\.){1,3}[a-z0-9]+"
reSMILEYS  = re.compile(r"[<=>]?[X:B8][\-o]?[)(ODPp\]\[]",  re.UNICODE)
reWORDS    = re.compile(r'\b\w+\b',  re.UNICODE)
reWORD_SEP = re.compile(r'[\.,;!?+=\-()\[\]"'+r"\':/]+",    re.UNICODE)
reBOT      = re.compile(r'@bot@',    re.UNICODE)
reUSER     = re.compile(r'@user@',   re.UNICODE)

class Masker:
    """A class to mask some sub-strings from a string, and to unmask them later"""
    def __init__(self, re, name="dodge"):
        """re is a compiled regular expression, which find the sub-strings to dodge
        in a string"""
        self.re      = re
        self.sub     = {}    # numbered keys => substrings
        self.name    = name

    def mask(self, toMask):
        """Mask the substrings.
        Return the string with substrings replaced by azazanameNazaza"""
        result    = toMask
        iterator  = self.re.finditer(toMask)
        i         = 0
        for match in iterator:
            i  += 1
            key = "azaza"+self.name+str(i)+"azaza"
            self.sub[key]    = match.group()
            result           = result.replace(self.sub[key], key, 1)
        return result

    def unmask(self, toUnmask):
        """Unmask the substrings, according to self.sub"""
        result    = toUnmask
        for key in self.sub:
            result = result.replace(key, self.sub[key])
        return result


class Entry:
    """An entry is a line of input.

    It has to be parsed into sentences, sentences into tokens, and tokens
    join to expressions.
    """
    def __init__(self,entry,username="User",botname="Ector"):
        """To create an Entry, one needs a line string

        Replace the botname in the line by "@bot@", and username by "@user@"
        """
        # Use a re, with \b around names to avoid replacing part of words,
        # like director -> dir@bot@.
        # See http://docs.python.org/dev/howto/regex.html
        reBotname  = re.compile(r'\b'+botname+r'\b',  re.IGNORECASE|re.LOCALE)
        reUsername = re.compile(r'\b'+username+r'\b', re.IGNORECASE|re.LOCALE)
        self.entry = reBotname.sub('@bot@', entry)
        self.entry = reUsername.sub('@user@', self.entry)
        self.sentences = None

    def getIndices(self, haystack):
        """Get all indices of sep in the string haystack.

        haystack: the string to search"""
        iterator = reSENTENCES_SEPARATORS.finditer(haystack)

        indices  = []
        for match in iterator:
            indices += [match.end()]

        if len(indices) and indices[-1] == '':
            return indices[:-1]
        else:
            return indices

    def getSentences(self):
        """Split the line of the entry into sentences.

        Needs to extract URLs and mails: http://xxx.xx.xx/.... and ggg@ggg.kk...,
        in order to avoid cutting a phrase because of the dots."""
        # If sentences are not yet computed
        if not self.sentences:
            # Get the URL and the mails, and replace them
            # Get the acronyms ############################
            acronyms   = Masker(reACRONYMS, "acronym")
            self.entry = acronyms.mask(self.entry)
            # Get the mails ###############################
            mails        = Masker(reMAIL, "mail")
            self.entry   = mails.mask(self.entry)
            # Get the URL #################################
            urls        = Masker(reURL, "url")
            self.entry  = urls.mask(self.entry)

            # Get the indices of the sentence separators. ###########
            idx = self.getIndices(self.entry)
            # Build the list of sentences, from the separators.
            self.sentences = []
            h = 0
            for i in idx:
                self.sentences += [self.entry[h:i].replace("\n"," ").strip()]
                h = i
            if h < len(self.entry):
                self.sentences += [self.entry[h:].replace("\n"," ").strip()]

            # Replace the locations of the URL and mails with the values
            for i in range(len(self.sentences)):
                # Put the acronyms back
                self.sentences[i] = acronyms.unmask(self.sentences[i])
                # Put the mails back
                self.sentences[i] = mails.unmask(self.sentences[i])
                # Put the URLs back
                self.sentences[i] = urls.unmask(self.sentences[i])
        return self.sentences

    def getPositions(self,sentence,regex):
        """Get the positions give by the regular expression regex in the sentence."""
        iterator    = regex.finditer(sentence)
        pos         = [match.span() for match in iterator]
        return pos

    def getSmileys(self,tokens):
        """Get smileys from punctuation tokens

        Tokens is a list of tokens (order is important)

        For example, when a token contains ":).", it should be separated
        into ":)" and "."

        Example:
        ['This', 'should', 'work', 'too', ':).']
        should be separated into:
        ['This', 'should', 'work', 'too', ':)', '.']
        """
        result = []
        for token in tokens:
            iterator = reSMILEYS.finditer(token)
            i, j    = 0, 0    # Positions of previous token part
            for match in iterator:
                if match.start() > j:
                    result += [token[i:j], token[match.start():match.end()]]
                else:
                    result += [token[match.start():match.end()]]
                (i, j)    = match.span()
            if j < len(token):
                result += [token[j:]]
        return result

    def getTokens(self, sentence):
        """Get the tokens of one sentence.

        A token can be:
        - a word
        - a punctuation mark (or several concateneted)
        - a smiley
        - a @bot@
        - a @user@"""
        smileys     = Masker(reSMILEYS, "smiley")
        sentence    = smileys.mask(sentence)
        bots        = Masker(reBOT, "bot")
        sentence    = bots.mask(sentence)
        users       = Masker(reUSER, "user")
        sentence    = users.mask(sentence)
        # Get the words' positions
        posWords  = self.getPositions(sentence, reWORDS)
        # Get the separators's positions
        posSep    = self.getPositions(sentence, reWORD_SEP)
        # Join the positions
        pos = posWords + posSep
        pos.sort()
        # Build the list of tokens from positions
        tokens = []
        for span in pos:
            tokens += [sentence[span[0]:span[1]].strip()]
        tokens    = self.getSmileys(tokens)
        tokens    = [smileys.unmask(token) for token in tokens]
        tokens    = [bots.unmask(token) for token in tokens]
        tokens    = [users.unmask(token) for token in tokens]
        return tokens

if __name__ == "__main__":
    e = Entry("Un. Deux? Trois!! Quatre.")
    print e.getSentences()