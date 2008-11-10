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
"""Definitions of the Concept Network classes.

A ConceptNetwork is a graph of nodes and links.
Each node gets a type.
"""
__author__    = "François Parmentier (parmentierf@users.sourceforge.net)"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2008 François Parmentier"
__license__   = "GPL"

from math import log, exp
import random
import time
import pickle

class ConceptNetworkError(Exception): pass
class ConceptNetworkNodeTypeError(ConceptNetworkError): pass
class ConceptNetworkUnknownNode(ConceptNetworkError): pass
class ConceptNetworkBadType(ConceptNetworkError): pass
class ConceptNetworkIncompleteLink(ConceptNetworkError): pass
class ConceptNetworkLackingParameter(ConceptNetworkError): pass
class ConceptNetworkBadParameter(ConceptNetworkError): pass
class ConceptNetworkNodeStateBadValue(ConceptNetworkError): pass
class ConceptNetworkStateBadType(ConceptNetworkError): pass
class TemperatureNoItems(ConceptNetworkError): pass
class TemperatureBadValue(ConceptNetworkError): pass


class ConceptNetwork:
    """A ConceptNetwork is a graph of nodes and links.

    Each node can be in a NodeState.
    """

    def __init__(self):
        self.node  = {}             # (symbol,type)     -> node
        self.link  = {}             # (from,to,label)   -> link
        self.state = {}             # state id          -> state

    def __hasType(self,obj,strType):
        "Verify strType of the obj"
        if not obj:
            raise ConceptNetworkLackingParameter,"There lacks a "+strType+"!"
        if obj.__class__.__name__ != strType:
            raise ConceptNetworkBadType,"Not a "+strType+"!"

    def getNode(self,symbol,type="basic"):
        """Get the node from the concept network whose symbol and type are given

        str symbol: symbol of the node
        str type:   name of the wanted type"""
        try:
            return self.node[(symbol,type)]
        except:
            raise ConceptNetworkUnknownNode,"Unknown node: \"" + symbol + "\" (" + type + ")"

    def addNode(self,node):
        "Add a Node to the Concept Network"
        symbol = node.getSymbol()
        type   = node.getTypeName()
        if (symbol,type) in self.node:
            #self.node[(symbol,type)].incrementOcc()
            self.node[(symbol, type)].addNode(node)
        else:
            self.node[(symbol,type)] = node

    def showNodes(self):
        "Show all the nodes in the Concept Network"
        for (symbol, type) in self.node:
            print "%s (%s): %d" % (symbol, type, self.getNode(symbol,type).getOcc())

    def showLinks(self,stateId=None):
        "Show all the links in the Concept Network"
        for (fro,to,label) in self.link:
            if label:
                if not stateId:
                    print "%10s -(%10s %d)-> %10s" % (fro.getSymbol(),
                                                   label.getSymbol(),
                                                   self.link[(fro,to,label)].getWeight() * 100,
                                                   to.getSymbol())
                else:
                    state = self.getState(stateId)
                    print "%10s -(%10s %d)-> %10s" % (fro.getSymbol(),
                                                   label.getSymbol(),
                                                   self.link[(fro,to,label)].getWeight(state) * 100,
                                                   to.getSymbol())
            else:
                print "%10s ------(%d)-------> %10s" % (fro.getSymbol(),
                                         self.link[(fro,to,label)].getWeight() * 100,
                                         to.getSymbol())

    def getLink(self,nodeFrom,nodeTo,nodeLabel=None):
        "Get the link going from nodeFrom to nodeTo, through nodeLabel (if it exists)"
        if not nodeFrom or not nodeTo:
            raise ConceptNetworkIncompleteLink,"There lacks at least one node!"
        self.__hasType(nodeFrom,"Node")    # Maybe this is not right for derived Nodes
        self.__hasType(nodeTo,  "Node")    # Maybe this is not right for derived Nodes
        if nodeLabel:
            self.__hasType(nodeLabel,"Node")    # Maybe this is not right for derived Nodes
        return self.link[(nodeFrom,nodeTo,nodeLabel)]

    def getLinksFrom(self,nodeFrom):
        "Get links that go from nodeFrom"
        self.__hasType(nodeFrom,"Node")    # Maybe this is not right for derived Nodes
        return [self.link[link] for link in self.link if link[0] == nodeFrom]

    def getLinksLabeled(self,nodeLabel):
        "Get links that go through nodeLabel, or from this node"
        self.__hasType(nodeLabel,"Node")    # Maybe this is not right for derived Nodes
        return [self.link[link] for link in self.link if link[2] == nodeLabel]

    def getLinksLabeledOrTo(self,nodeLabel):
        "Get links that go through nodeLabel, or to this node."
        self.__hasType(nodeLabel,"Node")    # Maybe this is not right for derived Nodes
        return [self.link[link] for link in self.link
                if link[2] == nodeLabel or link[1] == nodeLabel]

    def getLinksTo(self,nodeTo):
        """Get links clone that go to @a nodeTo.
           Don't get the !part_of! links."""
        self.__hasType(nodeTo,"Node")    # Maybe this is not right for derived Nodes
        return [self.link[link] for link in self.link if link[1] == nodeTo]

    def addLink(self,nodeFrom, nodeTo, nodeLabel=None):
        """Add a directional link to the ConceptNetwork.

        If the link already exists, its co-occurrence is incremented.
        If there is no label node, None should be passed as labelNode."""
        if not nodeFrom or not nodeTo:
            raise ConceptNetworkIncompleteLink,"There lacks at least one node!"
        self.__hasType(nodeFrom,"Node")    # Maybe this is not right for derived Nodes
        self.__hasType(nodeTo,  "Node")    # Maybe this is not right for derived Nodes
        if nodeLabel:
            self.__hasType(nodeLabel,"Node")    # Maybe this is not right for derived Nodes
        newLink = (nodeFrom,nodeTo,nodeLabel)
        if newLink in self.link:
            self.link[newLink].incrementCoOcc()
        else:
            self.link[newLink] = Link(nodeFrom,nodeTo,nodeLabel)
        return self.link[newLink]

    def addBidirectionalLink(self,node1, node2, nodeLabel=None):
        """Add a directional link to the ConceptNetwork.


        If the link already exists, its co-occurrence is incremented.
        If there is no label node, NULL should be passed as labelNode."""
        self.addLink(node1,node2,nodeLabel)
        self.addLink(node2,node1,nodeLabel)

    def addState(self,state):
        """Add a state to the Concept Network"""
        self.__hasType(state,"State")
        stateId = state.id
        if stateId in self.state.keys():
            raise ConceptNetworkDuplicateState, \
                  "The state ("+stateId+") already exists!"
        self.state[stateId] = state

    def getState(self,stateId):
        """Get the state of the Concept Network which id is stateId"""
        return self.state[stateId]

    def propagateActivations(self,state,
                             normalNumberComingLinks,
                             memoryPerf = 80):
        """Propagates activation values within the state

        state: in which activation values are found and changed
        normalNumberComingLinks "normal" number of links for the
                            whole influence to be taken into account
                            (must be > 1)
        memoryPerf: memory performance (the higher, the better)"""
        self.__hasType(state,"State")
        if normalNumberComingLinks <= 1:
            raise ConceptNetworkBadParameter, "normalNumberComingLinks must be > 1"
        # Set the old activation values as the current ones
        # Increment age of the nodes
        for symbol, nodeState in state.nodeState.iteritems():
            self.__hasType(nodeState,"NodeState")
            nodeState.ageActivationValues()

        for (symbol,typeName), node in self.node.iteritems():
            influence   = 0
            nbIncomings = 0
            newAv       = 0
            nodeState   = state.getNodeState(symbol,typeName)
            oldAV       = nodeState.getOldActivationValue()
            age         = nodeState.getAge()
            occ         = node.getOcc()
            links       = self.getLinksTo(node)
            # Compute the influence coming to the node
            for link in links:
                fromSymbol  = link.getNodeFrom().getSymbol()
                fromTypeName = link.getNodeFrom().getTypeName()
                fromState   = state.getNodeState(fromSymbol,fromTypeName)
                fromAV      = fromState.getOldActivationValue()
                weight      = link.getWeight(state)
                influence  += fromAV * weight
                nbIncomings+= 1
            #Compute the new activation value of the node
            influence   /= log(normalNumberComingLinks + nbIncomings) \
                         / log(normalNumberComingLinks)
            decay       = node.getDecay()
            minusAge    = 200 / (1+exp(-age / memoryPerf)) - 100
            newAV   = oldAV - decay * oldAV / 100 + influence - minusAge
            if newAV > 100: newAV = 100
            if newAV < 0:   newAV = 0
            nodeState.setActivationValue(newAV)

    def fastPropagateActivations(self,state,
                                 normalNumberComingLinks = 2,
                                 memoryPerf = 80):
        """Propagates activation values within state.

        Propagates activation values within state (faster than
        propagateActivations).

        state: in which activation values are found and changed
        normalNumberComingLinks "normal" number of links for the
                            whole influence to be taken into account
        memoryPerf: memory performance (the higher, the better)"""
        influenceValues = {}    # (symbol, type)    => influence value
        influenceNb     = {}    # (symbol, type)    => influence nb
        for nodeId, nodeState in state.nodeState.iteritems():
            nodeState.ageActivationValues()

        ## Fill influence table ##
        # Get the nodes influenced by others
        for (symbol,typeName), node in self.node.iteritems():
            if symbol:
                ov  = state.getNodeOldActivationValue(symbol,typeName)
                links = self.getLinksFrom(node)
                for link in links:
                    weight     = link.getWeight(state)
                    nodeTo     = link.getNodeTo()
                    linkSymbol = nodeTo.getSymbol()
                    linkTypeName = nodeTo.getTypeName()
                    inflNb     = linkSymbol in influenceNb and \
                                 influenceNb[(linkSymbol, linkTypeName)] \
                                 or 0
                    infl       = linkSymbol in influenceValues and \
                                 influenceValues[(linkSymbol,linkTypeName)] \
                                 or 0
                    infl      += 0.5 + ov * weight
                    influenceValues[(linkSymbol,linkTypeName)] = infl
                    influenceNb[(linkSymbol,linkTypeName)]     =   \
                                    (linkSymbol in influenceNb and \
                                     influenceNb[(linkSymbol,linkTypeName)] or 0) \
                                     + 1

        ## For all nodes in the state ##
        influenceValueKeys = influenceValues.keys()
        for (symbol, typeName) in state.nodeState:
            nodeState = state.getNodeState(symbol,typeName)
            oldAV    = nodeState.getOldActivationValue()
            node     = self.getNode(symbol, typeName)
            age      = nodeState.getAge()
            decay    = node.getDecay()
            minusAge = 200 / (1 + exp(-age / memoryPerf)) - 100
            # If this node is not influenced at all
            if not (symbol,typeName) in influenceValueKeys:
                newAV    = oldAV - decay * oldAV / 100 - minusAge
            # If this node receives influence
            else:
                influence   = influenceValues[(symbol,typeName)]
                nbIncomings = influenceNb[(symbol,typeName)]

                influence  /= log(normalNumberComingLinks + nbIncomings) \
                              / log(normalNumberComingLinks)

                newAV       = oldAV - decay * oldAV / 100 + influence \
                              - minusAge
            if newAV > 100: newAV = 100
            if newAV < 0:   newAV = 0
            nodeState.setActivationValue(newAV)

    def dump(self,file,protocol=2):
        """Dump the Concept Network in the file

        File must be opened. File is not closed by the method.
        Only nodes and links are saved, no state."""
        states = self.state.copy()
        self.removeAllStates()
        pickle.dump(self,file,protocol)
        self.state = states

    def removeAllStates(self):
        "Remove all states from the ConceptNetwork"
        self.state.clear()

    def removeStatesExcept(self,stateId):
        """Remove all states from the ConceptNetwork except the one which
        id is given.

        id: id of the State the keep.
        """
        stateToKeep = self.getState(stateId)
        self.removeAllStates()
        self.state[stateId] = stateToKeep

    def showStates(self):
        """Show all states id"""
        print "States (%d)" % (len(self.state))
        for id in self.state:
            print "\t%s" % (id)


class Node:
    """A ConceptNetworkNode is

    occ:    Occurrence of the node
    type:   Type name of the node (basic here)
    decay:  Decay rate of this type of node
    symbol: Symbol of the node.

    A node is identified by its type and name.

    see ConceptNetwork.addNode.

    This class is the base Node class.
    Every derived class must redefine:
    - getDecay()
    - getTypeName()
    """
    __type    = "basic"
    __decay   = 40

    def __init__(self, symbol, occ=1):
        self.symbol = symbol
        self.occ = occ

    def incrementOcc(self):
        self.occ = self.occ + 1

    def addNode(self, node):
        """Add the characteristics of the node to self.

        Typically, add the occ of the node to self.
        To be specialized..."""
        self.occ += node.getOcc()

    def getSymbol(self):
        "Get the symbol of the node"
        return self.symbol

    def getOcc(self):
        return self.occ

    def getTypeName(self):
        return self.__type

    def getDecay(self):
        "Get the decay rate of this node"
        return self.__decay


class Link:
    """Type of the a Concept Network node

    A ConceptNetwork.Link:
    - NodeFrom: the node from which the link comes
    - NodeTo  : the node to which the link goes
    - Label   : (optional) the node labelling the link
    - CoOcc   : the co-occurrence of the two nodes.

    See ConceptNetwork.addLink
    """

    def __init__(self,nodeFrom,nodeTo,nodeLabel=None,coOcc=1):
        if not nodeFrom or not nodeTo:
            raise ConceptNetworkIncompleteLink,"There lacks at least one node!"
        self.coOcc = coOcc
        self.fro   = nodeFrom       # from is a reserved keyword
        self.to    = nodeTo
        self.label = nodeLabel

    def incrementCoOcc(self):
        "Increment the co-occurrence of the link by 1"
        self.coOcc = self.coOcc  + 1

    def getCoOcc(self):
        return self.coOcc

    def getWeight(self, state=None):
        """Compute the weight of the link, and return it

        state: state of the concept network used to compute the weight"""
        labelAV = None
        occ     = self.fro.getOcc()
        weight  = float(self.coOcc) / occ
        if self.label and state:
            symbol = self.label.getSymbol()
            labelAV = state.getNodeActivationValue(symbol)
            weight += (1 - weight) * labelAV / 100
        return weight

    def getNodeFrom(self):
        return self.fro

    def getNodeTo(self):
        return self.to

    def getNodeLabel(self):
        return self.label


class State:
    """   A ConceptNetwork.State is the state of each activated nodes.

    Each State has an id (which could be the name of an ECTOR's user).
    This id is a python builtin type

    A State holds the state of all Nodes which are or have been recently
    activated.

    The State keeps the link between a node's symbol and typeName to its
    NodeState.
    """

    def __init__(self,stateId):
        self.id        = stateId
        self.nodeState = {}         # (node symbol, node type) -> node state

    def getNodeState(self,symbol,type="basic"):
        """Get the the state of the node which symbol is given.

        If the state did not exist, it is created with default arguments.
        """
        if (symbol,type) not in self.nodeState:
            self.nodeState[(symbol,type)] = NodeState()
        self.checkNodes()
        return self.nodeState[(symbol,type)]

    def setNodeActivationValue(self,activationValue,symbol,type="basic"):
        """Set the activationValue to the node which symbol is given in Concept Network State."""
        nodeState = self.getNodeState(symbol,type)
        self.__hasType(nodeState,"NodeState")
        if activationValue:
            nodeState.setActivationValue(activationValue)
        else:
            # If it is deleted, the age is no more known
            age = nodeState.age
            if age > 50:
                self.nodeState.pop((symbol,type))

    def getNodeActivationValue(self,symbol,type="basic"):
        """Get the activationValue of the node which symbol is given from Concept Network State."""
        nodeState = self.getNodeState(symbol,type)
        if nodeState.__class__.__name__ != "NodeState":
            raise ConceptNetworkStateBadType, \
                "The state of \""+symbol+"\" is not a NodeState!"
        return nodeState.getActivationValue()

    def getNodeOldActivationValue(self,symbol,type="basic"):
        """Get the old activationValue of the node which symbol is given from Concept Network State."""
        nodeState = self.getNodeState(symbol,type)
        return nodeState.getOldActivationValue()

    def getAverageActivationValue(self):
        "Get the average activation value"
        activationValues = [nodeState.getActivationValue()
                            for nodeId, nodeState in self.nodeState.iteritems()]
        nb  = len(activationValues)
        sum = sum(activationValues)
        if nb:  return sum / nb
        else:   return 0

    def getMaximumActivationValue(self, cn, typeNames):
        """Get the maximum activation value of the state, within nodes of types given by typeNames

        typeNames: names of the types to take into account
        cn:        Concept Network containing the nodes"""
        activationValues = [nodeState.getActivationValue()
                            for (symbol,typeName), nodeState in self.nodeState.iteritems()
                            if typeName in typeNames]
        return max(activationValues)

    def getActivatedTypedNodes(self, cn, typeNames, threshold=90):
        """Get the activated nodes of cn.

        The returned nodes must be in the list of typeNames, and
        have an activation value greater than threshold

        Return a list of tuples (node,activation value)"""
        nodes = []
        for nodeId, node in cn.node.iteritems() :
            (symbol, typeName) = nodeId
            av      = self.getNodeActivationValue(symbol,typeName)
            if av > threshold:
                if typeName in typeNames:
                    nodes = nodes + [(node,av)]
        return nodes

    def __hasType(self,obj,strType):
        "Check that object has the typeName"
        if not obj:
            raise ConceptNetworkLackingParameter,"There lacks a "+strType+"!"
        if obj.__class__.__name__ != strType:
            raise ConceptNetworkBadType,"Not a "+strType+"!"

    def checkNodes(self):
        "Check that the nodes are NodeState s"
        for nodeId, nodeState in self.nodeState.iteritems():
            self.__hasType(nodeState,"NodeState")

    def showNodes(self):
        "Print the node states"
        print "oldav\tav\tage\tNode"
        for (symbol,typeName) in self.nodeState:
            nodeState = self.nodeState[(symbol,typeName)]
            print "%d\t%d\t%d\t%s(%s)" % (nodeState.getOldActivationValue(),
                              nodeState.getActivationValue(),
                              nodeState.getAge(),
                              symbol, typeName)


class NodeState:
    """The state of a node (activation value, old activation value, age)

    Each node in the state has:
    - an age (which is the number of propagations since the last
     complete activation of the node)
    - an activationValue
    - an odlActivationValue (used during propagation).
    """
    def __init__(self, activationValue=0, age=0):
        self.oldActivationValue = 0
        self.activationValue    = activationValue
        self.age                = age

    def setActivationValue(self,activationValue):
        if activationValue < 0:
            raise ConceptNetworkNodeStateBadValue, \
                "An activation value of "+activationValue+" is not allowed! Must be in [0,100]"
        if activationValue > 100:
            raise ConceptNetworkNodeStateBadValue, \
                "An activation value of "+activationValue+" is not allowed! Must be in [0,100]"
        self.oldActivationValue = self.activationValue
        self.activationValue    = activationValue

    def getActivationValue(self):
        if self.activationValue < 0:
            raise ConceptNetworkNodeStateBadValue, \
                "An activation value of "+self.activationValue+" is not allowed! Must be in [0,100]"
        if self.activationValue > 100:
            raise ConceptNetworkNodeStateBadValue, \
                "An activation value of "+self.activationValue+" is not allowed! Must be in [0,100]"
        return self.activationValue

    def ageActivationValues(self):
        "Set the old activation value to the activation value, and increment age"
        self.incrementAge()
        self.oldActivationValue = self.activationValue

    def getOldActivationValue(self):
        return self.oldActivationValue

    def resetAge(self):
        self.age = 0

    def incrementAge(self):
        self.age += 1

    def getAge(self):
        return self.age


class Temperature:
    "Class for chosing among weighted items according to a temperature"
    def __init__(self,temperature,influence=2):
        """Initialize the temperature value

        The higher, the more deterministic the choices
        (0<= temperature <= 100)"""
        if temperature < 0 or temperature > 100:
            raise TemperatureBadValue, "Bad temperature! (must be in [0,100])"
        self.value      = temperature
        self.influence  = influence

    def randomize(self):
        t = time.time()
        random.seed(t)

    def setValue(self,value):
        self.value = value

    def getValue(self):
        return self.value

    def chooseWeightedItem(self,items):
        """Choose and return one node among the weighted items given,
        according to the temperature value

        items: list of tuples (item, weight)

        Each item must have a getSymbol() method, which returns a string.

        returns the chosen item"""
        nb  = len(items)
        T   = (self.value - 50) / 50.0
        if nb == 0: raise TemperatureNoItems, "No items were given!"
        total = sum([weight for (item, weight) in items])
        avg = total / float(nb)
        ur  = {}

        urgencySum = 0
        for (item, weight) in items:
            urgency = weight + T * self.influence * (avg - weight)
            if urgency < 0: urgency = 0
            urgencySum += urgency
            ur[item.getSymbol()] = urgencySum

        if urgencySum < 1: urgencySum = 1
        choice = random.randint(0,urgencySum)

        for (item, weight) in items:
            symbol  = item.getSymbol()
            urgency = ur[symbol]
            if choice <= urgency:
                return item
        return item[0]


# main
def main():
    import os
    from optparse import OptionParser

    usage="usage: %prog [-h]"
    parser = OptionParser(usage=usage,version="%prog 0.1")
    parser.add_option("-f", "--file", dest="filename", default="conceptnetwork.pkl",
                      help="open the file as a Concept Network")
    (options, args) = parser.parse_args()

    filename    = options.filename

    if os.path.exists(filename):
        f = open(filename)
        try:
            cn = pickle.load(f)
        finally:
            f.close()
    else:
        cn = ConceptNetwork()
    state    = State(1)
    cn.addState(state)

    while True:
        line = sys.stdin.readline().strip()
        if sys.stdin.closed:
            break
        if line[:9] == "@addnode ":
            node = Node(line[9:])
            cn.addNode(node)
            print "Node \"%s\" added" % (line[9:])
        elif line[:9] == "@addlink ":
            params = line[9:].split()
            if len(params) == 2:
                try:
                    node1 = cn.getNode(params[0])
                except ConceptNetworkUnknownNode:
                    print "The node \"%s\" does not exist!" % (params[0])
                    continue
                try:
                    node2 = cn.getNode(params[1])
                except ConceptNetworkUnknownNode:
                    print "The node \"%s\" does not exist!" % (params[1])
                    continue
                print cn.addLink(node1,node2)
            elif len(params) == 3:
                node1 = cn.getNode(params[0])
                node2 = cn.getNode(params[1])
                node3 = cn.getNode(params[2])
                print cn.addLink(node1,node2,node3)
        elif line[:10] == "@shownodes":
            cn.showNodes()
        elif line[:10] == "@showlinks":
            cn.showLinks(1)
        elif line[:10] == "@activate ":
            params = line[10:].split()
            if len(params) == 1:
                state.setNodeActivationValue(100, params[0])
                nodeState = state.getNodeState(params[0])
                nodeState.resetAge()
            else:
                state.setNodeActivationValue(int(params[1]), params[0])
        elif line[:10] == "@showstate":
            state.showNodes()
        elif line[:10] == "@propagate":
            if len(line) > 10:
                nb = int(line[11:].strip())
                for i in range(0,nb):
                    cn.fastPropagateActivations(state)
            else:
                cn.fastPropagateActivations(state)
        elif line[:5] == "@save":
            # NOTE: the writing protocol must be the same than the reading one
            file = open(filename,"w")
            cn.dump(file, 0)
            file.close()
            file = open("state_1.pkl","w")
            pickle.dump(state,file,0)
            file.close()
            print "Concept Network saved in \"%s\"" % (filename)
        elif line.startswith("@quit"):
            return 0
        elif line[:5] == "@help":
            print """@help give this help
@addnode name: add the node given
@addlink node1 node2 [label]: add a link from node1 to node2
@activate name [activation value]: activate a node from its name
@propagate [nb]: propagate the activation nb times
@shownodes: show the nodes in the ConceptNetwork
@showlinks: show the links in the ConceptNetwork
@showstate: show the state of the nodes
@save: save the Concept Network and its state
@quit: quit without saving"""

if __name__ == "__main__":
    import sys

    status = main()
    sys.exit(status)