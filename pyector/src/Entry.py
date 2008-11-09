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
"""Definitions of the Entry class.

An entry is a line of input, which has to be parsed into sentences,
sentences into tokens, and tokens join to expressions.
"""
__author__    = "François Parmentier (parmentierf@users.sourceforge.net)"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2008 François Parmentier"
__license__   = "GPL"

SENTENCE_SEPARATORS = "!?."
WORD_SEPARATORS     = "/,'()[];:\"-+«»!?.<>="

import re

# From http://www.regular-expressions.info/email.html
MAIL_REGEXP = re.compile(r"([a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+(?:[A-Z]{2}|com|org|net|gov|mil|biz|info|mobi|name|aero|jobs|museum))",
                          re.IGNORECASE|re.MULTILINE)

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
        reSENTENCES_SEPARATORS = re.compile(r'[?!\.]+ *')
        iterator = reSENTENCES_SEPARATORS.finditer(haystack)

        indices  = []
        for match in iterator:
            indices += [match.end()]

        return indices[:-1]

    def getSentences(self):
        """Split the line of the entry into sentences.

        Needs to extract URLs and mails: http://xxx.xx.xx/.... and ggg@ggg.kk...,
        in order to avoid cutting a phrase because of the dots."""
        # If sentences are not yet computed
        if not self.sentences:
            # TODO: Get the URL and the mails, and replace them
            # Get the acronyms
            reACRONYMS = re.compile(r'(?:[A-Z]\.)+', re.LOCALE)
            iterator   = reACRONYMS.finditer(self.entry)
            acronyms   = {}
            i          = 0
            for match in iterator:
                i  += 1
                key = "@acro"+str(i)+"@"
                acronyms[key] = match.group()
                self.entry = self.entry.replace(acronyms[key], key, 1)
            pass
            # Get the indices of the sentence separators.
            idx = self.getIndices(self.entry)
            # Build the list of sentences, from the separators.
            self.sentences = []
            h = 0
            for i in idx:
                self.sentences += [self.entry[h:i].strip()]
                h = i
            self.sentences += [self.entry[h:].replace("\n"," ").strip()]
            #TODO: Replace the locations of the URL and mails with the values
            for i in range(len(self.sentences)):
                # Put the acronyms
                for key in acronyms:
                    self.sentences[i] = self.sentences[i].replace(key, acronyms[key])
            pass
        return self.sentences


if __name__ == "__main__":
    e = Entry("Un. Deux? Trois!! Quatre.")
    print e.getSentences()