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

class Entry:
    """An entry is a line of input.

    It has to be parsed into sentences, sentences into tokens, and tokens
    join to expressions.
    """
    def __init__(self,entry,botname="Ector",username="User"):
        """To create an Entry, one needs a line string

        Replace the botname in the line by "@bot@", and username by "@user@"
        """
        self.entry = entry.replace(botname,"@bot@")
        self.entry = self.entry.replace(username,"@user@")
        self.sentences = None

    def getIndices(self, haystack, sep, sepList):
        """Get all indices of sep in the string haystack.

        haystack: the string to search
        sep: the separator character
        sepList: list of the separators considered as part as the separator"""
        indices  = []
        previous = -1
        while True:
            try:
                i        = haystack.index(sep,previous+1)
            except ValueError:
                # if sep in not in the haystack
                break

            # Cat the separator characters
            if i+1 == len(haystack):
                # if it's the last character of the string
                break
            nextInSep = i+1 < len(haystack)
            if nextInSep:
                nextInSep = haystack[i+1] in sepList
            while nextInSep:
                i += 1
                # Stop if the end of the haystack is compound of separators
                nextInSep = i+1 < len(haystack)
                if nextInSep:
                    nextInSep = haystack[i+1] in sepList
                if not nextInSep:
                    return indices
            previous = i
            indices += [i]

        return indices

    def getSentences(self):
        """Split the line of the entry into sentences.

        Needs to extract URLs and mails: http://xxx.xx.xx/.... and ggg@ggg.kk...,
        in order to avoid cutting a phrase because of the dots."""
        # If sentences are not yet computed
        if not self.sentences:
            # TODO: Get the URL and the mails, and replace them
            pass
            # Get the indices of the sentence separators.
            idx = []
            for sep in SENTENCE_SEPARATORS:
                idx += self.getIndices(self.entry,sep,SENTENCE_SEPARATORS)
            idx.sort()
            # Build the list of sentences, from the separators.
            self.sentences = []
            h = 0
            for i in idx:
                self.sentences += [self.entry[h:i+1].strip()]
                h = i+1
            self.sentences += [self.entry[h:].strip()]
            #TODO: Replace the locations of the URL and mails with the values
            pass
        return self.sentences


if __name__ == "__main__":
    e = Entry("Un. Deux? Trois!! Quatre.")
    print e.getSentences()