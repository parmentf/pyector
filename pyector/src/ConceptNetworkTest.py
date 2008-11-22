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
"""Unit test for ConceptNetwork.py

This is the first python unit test I write... :P
"""

__author__    = "François Parmentier (parmentierf@users.sourceforge.net)"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2008 François Parmentier"
__license__   = "GPL"

from ConceptNetwork import *
import unittest


class NodeTest(unittest.TestCase):
    "Test the Node class"
    def testCreationOcc(self):
        "A just created node has an occurrence equals to 1"
        node = Node("Salut")
        self.assertEqual(1,node.getOcc())


class ConceptNetworkTest(unittest.TestCase):
    "Test the ConceptNetwork class"
    def testConceptNetworkGetNode(self):
        "Test getting a node from a Concept Network after adding it"
        cn    = ConceptNetwork()
        node1 = Node("Salut")
        cn.addNode(node1)
        self.assertEqual(node1, cn.getNode("Salut","basic"))

    def testConceptNetworkGetNodeTyped(self):
        "Test getting a node with a type"
        class TestNode(Node):
            __type  = "test"
            __decay = 35
            def __init__(self, symbol, occ = 1):
                Node.__init__(self, symbol, occ=occ)
            def getTypeName(self):
                return self.__type
            def getDecay(self):
                return self.__decay
        cn    = ConceptNetwork()
        node1 = TestNode("Salut.")
        cn.addNode(node1)
        self.assertEqual(node1, cn.getNode("Salut.","test"))
        self.assertEqual("test", node1.getTypeName())

    def testConceptNetworkGetUnkownNode(self):
        "Test whether an unknown node raises an exception"
        cn = ConceptNetwork()
        self.assertRaises(ConceptNetworkUnknownNode,cn.getNode,"Nimp")

    def testConceptNetworkGetBadLink(self):
        "A link has at least 2 nodes"
        cn = ConceptNetwork()
        self.assertRaises(ConceptNetworkIncompleteLink,cn.getLink,None,None)

    def testConceptNetworkAddNodeTwice(self):
        "One node added twice implies an incremented occ"
        cn   = ConceptNetwork()
        node = Node("Salut")
        cn.addNode(node)
        cn.addNode(node)
        self.assertEqual(2,node.getOcc())

    def testConceptNetworkGetLinksFrom(self):
        "Get links from a node"
        cn = ConceptNetwork()
        nodeFrom = Node("From")
        nodeTo1  = Node("To1")
        nodeTo2  = Node("To2")
        nodeTo3  = Node("To3")
        nodeLabel= Node("Label")
        cn.addLink(nodeFrom, nodeTo1)
        cn.addLink(nodeFrom, nodeTo2)
        cn.addLink(nodeFrom, nodeTo3, nodeLabel)
        links = cn.getLinksFrom(nodeFrom)
        self.assertEqual(3,len(links))

    def testConceptNetworkGetLinksLabeled(self):
        "Get links with a label"
        cn = ConceptNetwork()
        nodeFrom = Node("From")
        nodeTo1  = Node("To1")
        nodeTo2  = Node("To2")
        nodeTo3  = Node("To3")
        nodeLabel= Node("Label")
        cn.addLink(nodeFrom, nodeTo1,nodeLabel)
        cn.addLink(nodeFrom, nodeTo2)
        cn.addLink(nodeFrom, nodeTo3, nodeLabel)
        links = cn.getLinksLabeled(nodeLabel)
        self.assertEqual(2,len(links))

    def testConceptNetworkGetLinksLabeledOrTo(self):
        "Get links with a label or to that label"
        cn = ConceptNetwork()
        nodeFrom = Node("From")
        nodeTo1  = Node("To1")
        nodeTo2  = Node("To2")
        nodeLabel= Node("Label")
        cn.addLink(nodeFrom, nodeTo1)
        cn.addLink(nodeFrom, nodeLabel)
        cn.addLink(nodeFrom, nodeTo2, nodeLabel)
        links = cn.getLinksLabeledOrTo(nodeLabel)
        self.assertEqual(2,len(links))

    def testConceptNetworkGetLinksTo(self):
        "Get links to a node"
        cn = ConceptNetwork()
        nodeFrom = Node("From")
        nodeTo1  = Node("To1")
        nodeTo2  = Node("To2")
        nodeLabel= Node("Label")
        cn.addLink(nodeFrom, nodeTo1)
        cn.addLink(nodeFrom, nodeTo2)
        cn.addLink(nodeFrom, nodeTo2, nodeLabel)
        links = cn.getLinksTo(nodeTo2)
        self.assertEqual(2,len(links))

    def testPropagation(self):
        "Test the propagation"
        conceptNetwork = ConceptNetwork()
        nodeFrom = Node("From")
        nodeTo1  = Node("To1")
        conceptNetwork.addNode(nodeFrom)
        conceptNetwork.addNode(nodeTo1)
        conceptNetwork.addLink(nodeFrom, nodeTo1)
        state = State(1)
        conceptNetwork.addState(state)
        state.setNodeActivationValue(100,"From","basic")
        conceptNetwork.propagateActivations(state,2)
        self.assertEqual(True,state.getNodeActivationValue("To1","basic") > 50)

    def testFastPropagation(self):
        "Test the propagation"
        conceptNetwork = ConceptNetwork()
        nodeFrom = Node("From")
        nodeTo1  = Node("To1")
        conceptNetwork.addNode(nodeFrom)
        conceptNetwork.addNode(nodeTo1)
        conceptNetwork.addLink(nodeFrom, nodeTo1)
        state = State(1)
        conceptNetwork.addState(state)
        state.setNodeActivationValue(100,"From","basic")
        conceptNetwork.fastPropagateActivations(state,2)
        self.assertEqual(True,state.getNodeActivationValue("To1") > 50)

    def testDumpLoad(self):
        "Test the saving of the Concept Network"
        conceptNetwork = ConceptNetwork()
        nodeFrom = Node("From")
        nodeTo1  = Node("To1")
        conceptNetwork.addNode(nodeFrom)
        conceptNetwork.addNode(nodeTo1)
        conceptNetwork.addLink(nodeFrom, nodeTo1)
        state = State(1)
        conceptNetwork.addState(state)
        state.setNodeActivationValue(100,"From")
        conceptNetwork.fastPropagateActivations(state,2)
        av = state.getNodeActivationValue("To1")

        f = open("cntest.data","w")
        try:
            conceptNetwork.dump(f,0)
        finally:
            f.close()

        f = open("cntest.data")
        try:
            cnLoaded = pickle.load(f)
        finally:
            f.close()

        import os
        os.remove("cntest.data")

        # No state is dumped!
        self.assertRaises(KeyError,cnLoaded.getState,1)

        nodeLoaded = cnLoaded.getNode("To1")
        self.assertTrue(nodeLoaded)

    def testRemoveState(self):
        "Test ConceptNetwork.removeStatesExcept()"
        conceptNetwork = ConceptNetwork()
        state1         = State(1)
        state2         = State(2)
        conceptNetwork.addState(state1)
        conceptNetwork.addState(state2)
        conceptNetwork.removeStatesExcept(2)
        self.assertEqual(state2, conceptNetwork.getState(2))


class LinkTest(unittest.TestCase):
    "Test the Link class"
    def testCreateBadLink(self):
        "A link has at least 2 nodes"
        self.assertRaises(ConceptNetworkIncompleteLink,Link,None,None)

    def testCoOccLink(self):
        "Twice the same link -> its co-occurrence is incremented"
        conceptNetwork = ConceptNetwork()
        nodeFrom    = Node("from")
        nodeTo      = Node("to")
        conceptNetwork.addNode(nodeFrom)
        conceptNetwork.addNode(nodeTo)
        conceptNetwork.addLink(nodeFrom, nodeTo)
        link        = conceptNetwork.addLink(nodeFrom, nodeTo)
        self.assertEqual(2, link.getCoOcc())

    def testCoOccLink2(self):
        "Twice the same link -> its co-occurrence is incremented"
        conceptNetwork = ConceptNetwork()
        nodeFrom    = Node("from")
        nodeTo      = Node("to")
        conceptNetwork.addNode(nodeFrom)
        conceptNetwork.addNode(nodeTo)
        conceptNetwork.addLink(nodeFrom, nodeTo)
        nodeFrom2   = Node("from")
        nodeTo2     = Node("to")
        conceptNetwork.addNode(nodeFrom2)
        conceptNetwork.addNode(nodeTo2)
        link        = conceptNetwork.addLink(nodeFrom2, nodeTo2)
        self.assertEqual(2, link.getCoOcc())


class StateTest(unittest.TestCase):
    "Test the State class"
    def testCreateState(self):
        "A state can be created anytime, without arg"
        state = State(1)
        self.assertEqual(1,state.id)

    def testLinkWeight(self):
        "Test the weight of a link"
        cn    = ConceptNetwork()
        state = State(1)
        cn.addState(state)
        nodeFrom = Node("From")
        nodeTo   = Node("To")
        link = cn.addLink(nodeFrom,nodeTo)
        self.assertEqual(1,link.getWeight())

    def testLinkLabeledWeight(self):
        "Test the weight of a labeled link"
        cn    = ConceptNetwork()
        state = State(1)
        cn.addState(state)
        nodeFrom = Node("From")
        nodeTo   = Node("To")
        nodeLabel= Node("Label")
        link = cn.addLink(nodeFrom,nodeTo,nodeLabel)
        self.assertEqual(1,link.getWeight(state))

    def testGetNodeStateTyped(self):
        "Test getting a node state with a type"
        cn    = ConceptNetwork()
        node1 = Node("Salut.")
        cn.addNode(node1)
        state = State(1)
        cn.addState(state)
        state.setNodeActivationValue(100, "Salut.","basic")
        self.assertEqual(100, state.getNodeActivationValue("Salut.","basic"))

    def testAging(self):
        """See if a old node state is removed when too old.

        When a NodeState has more than 50 propagations, and that it is set to zero,
        it has to disappear from the state of the ConceptNetwork."""
        conceptNetwork = ConceptNetwork()
        nodeFrom = Node("From")
        nodeTo1  = Node("To1")
        conceptNetwork.addNode(nodeFrom)
        conceptNetwork.addNode(nodeTo1)
        conceptNetwork.addLink(nodeFrom, nodeTo1)
        state = State(1)
        conceptNetwork.addState(state)
        state.setNodeActivationValue(100,"From","basic")
        for i in range(0,51):
            conceptNetwork.fastPropagateActivations(state,2)
        state.setNodeActivationValue(0, "From", "basic")
        self.assertRaises(KeyError,state.nodeState.__getitem__,("From","basic"))


class TemperatureTest(unittest.TestCase):
    "Test the Temperature class"
    def testChooseWeightedItems(self):
        temperature = Temperature(50)
        node = Node("1")
        l = [(node,1)]
        self.assertEqual(node,temperature.chooseWeightedItem(l))
        node2 = Node("2")
        node3 = Node("3")
        l = [(node,2),(node2,2),(node3,2)]
        self.assertEqual(True,temperature.chooseWeightedItem(l) != None)

    def testCold(self):
        "When the temperature is cold, weight are reinforced"
        temperature = Temperature(0)
        node = Node("1")
        node2 = Node("2")
        l = [(node,100),(node2,1)]
        self.assertEqual(node,temperature.chooseWeightedItem(l))


if __name__ == "__main__":
	unittest.main()

