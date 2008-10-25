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

