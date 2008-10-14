#!/usr/bin/env python
# coding: utf-8

__author__    = "François Pamrentier (parmentierf@users.sourceforge.net)"
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
    
