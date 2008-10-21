#!/usr/bin/env python
# coding: utf-8
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
        node = Node("Salut",NodeType("token"))
        self.assertEqual(1,node.getOcc())

class NodeTypeTest(unittest.TestCase):
    "Test the NodeType class"
    def testRaiseBadType(self):
        "One cannot create an unknown type"
        self.assertRaises(ConceptNetworkNodeTypeError,NodeType,"Nimp")

class ConceptNetworkTest(unittest.TestCase):
    "Test the ConceptNetwork class"
    def testConceptNetworkGetNode(self):
        "Test getting a node from a Concept Network after adding it"
        cn    = ConceptNetwork()
        node1 = Node("Salut",NodeType("token"))
        cn.addNode(node1)
        self.assertEqual(node1, cn.getNode("Salut"))

    def testConceptNetworkGetUnkownNode(self):
        "Test whether an unknown node raises an exception"
        cn = ConceptNetwork()
        self.assertRaises(ConceptNetworkUnknownNode,cn.getNode,"Nimp")

    def testConceptNetworkAddBadTypeNode(self):
        "Add something else than a Node with addNode()"
        cn = ConceptNetwork()
        self.assertRaises(ConceptNetworkBadType,cn.addNode,"Nimp")

    def testConceptNetworkGetBadLink(self):
        "A link has at least 2 nodes"
        cn = ConceptNetwork()
        self.assertRaises(ConceptNetworkIncompleteLink,cn.getLink,None,None)

    def testConceptNetworkAddNodeTwice(self):
        "One node added twice implies an incremented occ"
        cn   = ConceptNetwork()
        node = Node("Salut",NodeType("token"))
        cn.addNode(node)
        cn.addNode(node)
        self.assertEqual(2,node.getOcc())

    def testConceptNetworkGetLinksFrom(self):
        "Get links from a node"
        cn = ConceptNetwork()
        nodeFrom = Node("From",NodeType("token"))
        nodeTo1  = Node("To1", NodeType("token"))
        nodeTo2  = Node("To2", NodeType("token"))
        nodeTo3  = Node("To3", NodeType("token"))
        nodeLabel= Node("Label",NodeType("token"))
        cn.addLink(nodeFrom, nodeTo1)
        cn.addLink(nodeFrom, nodeTo2)
        cn.addLink(nodeFrom, nodeTo3, nodeLabel)
        links = cn.getLinksFrom(nodeFrom)
        self.assertEqual(3,len(links))

    def testConceptNetworkGetLinksLabeled(self):
        "Get links with a label"
        cn = ConceptNetwork()
        nodeFrom = Node("From",NodeType("token"))
        nodeTo1  = Node("To1", NodeType("token"))
        nodeTo2  = Node("To2", NodeType("token"))
        nodeTo3  = Node("To3", NodeType("token"))
        nodeLabel= Node("Label",NodeType("token"))
        cn.addLink(nodeFrom, nodeTo1,nodeLabel)
        cn.addLink(nodeFrom, nodeTo2)
        cn.addLink(nodeFrom, nodeTo3, nodeLabel)
        links = cn.getLinksLabeled(nodeLabel)
        self.assertEqual(2,len(links))

    def testConceptNetworkGetLinksLabeledOrTo(self):
        "Get links with a label or to that label"
        cn = ConceptNetwork()
        nodeFrom = Node("From",NodeType("token"))
        nodeTo1  = Node("To1", NodeType("token"))
        nodeTo2  = Node("To2", NodeType("token"))
        nodeLabel= Node("Label",NodeType("token"))
        cn.addLink(nodeFrom, nodeTo1)
        cn.addLink(nodeFrom, nodeLabel)
        cn.addLink(nodeFrom, nodeTo2, nodeLabel)
        links = cn.getLinksLabeledOrTo(nodeLabel)
        self.assertEqual(2,len(links))

    def testConceptNetworkGetLinksTo(self):
        "Get links to a node"
        cn = ConceptNetwork()
        nodeFrom = Node("From",NodeType("token"))
        nodeTo1  = Node("To1", NodeType("token"))
        nodeTo2  = Node("To2", NodeType("token"))
        nodeLabel= Node("Label",NodeType("token"))
        cn.addLink(nodeFrom, nodeTo1)
        cn.addLink(nodeFrom, nodeTo2)
        cn.addLink(nodeFrom, nodeTo2, nodeLabel)
        links = cn.getLinksTo(nodeTo2)
        self.assertEqual(2,len(links))

    def testPropagation(self):
        "Test the propagation"
        conceptNetwork = ConceptNetwork()
        nodeFrom = Node("From",NodeType("token"))
        nodeTo1  = Node("To1", NodeType("token"))
        conceptNetwork.addNode(nodeFrom)
        conceptNetwork.addNode(nodeTo1)
        conceptNetwork.addLink(nodeFrom, nodeTo1)
        state = State(1)
        conceptNetwork.addState(state)
        state.setNodeActivationValue("From",100)
        conceptNetwork.propagateActivations(state,2)
        self.assertEqual(True,state.getNodeActivationValue("To1") > 50)

    def testFastPropagation(self):
        "Test the propagation"
        conceptNetwork = ConceptNetwork()
        nodeFrom = Node("From",NodeType("token"))
        nodeTo1  = Node("To1", NodeType("token"))
        conceptNetwork.addNode(nodeFrom)
        conceptNetwork.addNode(nodeTo1)
        conceptNetwork.addLink(nodeFrom, nodeTo1)
        state = State(1)
        conceptNetwork.addState(state)
        state.setNodeActivationValue("From",100)
        conceptNetwork.fastPropagateActivations(state,2)
        self.assertEqual(True,state.getNodeActivationValue("To1") > 50)

    def testDumpLoad(self):
        "Test the saving of the Concept Network"
        conceptNetwork = ConceptNetwork()
        nodeFrom = Node("From",NodeType("token"))
        nodeTo1  = Node("To1", NodeType("token"))
        conceptNetwork.addNode(nodeFrom)
        conceptNetwork.addNode(nodeTo1)
        conceptNetwork.addLink(nodeFrom, nodeTo1)
        state = State(1)
        conceptNetwork.addState(state)
        state.setNodeActivationValue("From",100)
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

        nodeLoaded = cnLoaded.node["To1"]
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
        nodeFrom = Node("From",NodeType("token"))
        nodeTo   = Node("To",  NodeType("token"))
        link = cn.addLink(nodeFrom,nodeTo)
        self.assertEqual(1,link.getWeight())

    def testLinkLabeledWeight(self):
        "Test the weight of a labeled link"
        cn    = ConceptNetwork()
        state = State(1)
        cn.addState(state)
        nodeFrom = Node("From",NodeType("token"))
        nodeTo   = Node("To",  NodeType("token"))
        nodeLabel= Node("Label",NodeType("token"))
        link = cn.addLink(nodeFrom,nodeTo,nodeLabel)
        self.assertEqual(1,link.getWeight(state))

class TemperatureTest(unittest.TestCase):
    "Test the Temperature class"
    def testChooseWeightedItems(self):
        temperature = Temperature(50)
        tokenType = NodeType("token")
        node = Node("1",tokenType)
        l = [(node,1)]
        self.assertEqual(node,temperature.chooseWeightedItem(l))
        node2 = Node("2",tokenType)
        node3 = Node("3",tokenType)
        l = [(node,2),(node2,2),(node3,2)]
        self.assertEqual(True,temperature.chooseWeightedItem(l) != None)

    def testCold(self):
        "When the temperature is cold, weight are reinforced"
        temperature = Temperature(0)
        tokenType = NodeType("token")
        node = Node("1",tokenType)
        node2 = Node("2",tokenType)
        l = [(node,100),(node2,1)]
        self.assertEqual(node,temperature.chooseWeightedItem(l))

if __name__ == "__main__":
	unittest.main()

