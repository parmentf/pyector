pyECTOR README file
===================
author parmentierf@users.sourceforge.net
0.4, 2008-12-11

Description
-----------
ECTOR is a learning chatterbot. pyECTOR is its Python version.

ECTOR learns from what people say. It is based on a artificial
intelligence architecture, that is inspired from Copycat, an AI
system from Mitchell and Hofstadter.

The Concept Network it uses is a mix between neural and semantic
networks. It uses co-occurences to compute the influence of one
semantic node on another. The links are statistically weighted.

So, ECTOR does not know anything at its "birth".
It's to you to teach it.

Prerequisites
-------------
pyECTOR is written in Python so you need a Python interpreter
(version 2.5 or later) to execute pyECTOR. Python is installed by
default in most Linux distributions.  You can download Python from
the official Python website http://www.python.org.

Obtaining pyECTOR
-----------------
The latest pyECTOR version and online documentation can be found at
http://pyector.googlecode.com/

Installation
------------
Once you've downloaded the file, untar it like that:
-------------------
tar -xvzf pyector-0.4.tar.gz .
-------------------

Version 0.4 allows Ector to answer, building original sentences
from what users said to it. Generated sentences may seem wrong
grammatically. Be indulgent with it, consider it like a child,
learning to speak.

----------
python ConceptNetwork.py
----------

It allows one to play with its internal mechanism: the
http://code.google.com/p/pyector/wiki/ConceptNetwork[Concept Network].

You can +@addnode+ (add a node), +@addlink+ (add a link between two
existing nodes), and even +@activate+ a node, so you can
+@propagate+ activation values, and +@showstate+.

A small reminder about the commands is obtained by typing +@help+.

See doc/html/ConceptNetworkModule.html.

Usage
-----
-------------------
python Ector.py [-p username][-n botname=Ector][-v|-q][-l logfilepath=ector.log][-s|-g][-h]
-------------------

Be aware that ECTOR does not know anything at the beginning (first launch).
You have to teach it all!
It learns from what you say (so be polite and write well, if you want ECTOR
to do so).

A small help is available from ECTOR prompt:
-------------------
User>@help
-------------------

From the prompt, you just have to speak to Ector.
-------------------
User>Hello!
Ector> Hello!
User>...
-------------------
The first sentences you will say will be echoed, but after some utterance,
Ector will begin to link words, and to create original answers.

Resources
---------
- http://pyector.googlecode.com/

COPYING
-------
Copyright (C) 2008 François Parmentier. Free use of this software
is granted under the terms of the GNU General Public License (GPL).
