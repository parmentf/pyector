#!/usr/bin/env python
# coding: utf-8
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

from math import *
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
    Each node gets a type.
    """
    def __init__(self):
        self.node  = {}             # symbol            -> node
        self.link  = {}             # (from,to,label)   -> link
        self.state = {}             # state id          -> state

    def __hasType(self,obj,strType):
        "Verify strType of the obj"
        if not obj:
            raise ConceptNetworkLackingParameter,"There lacks a "+strType+"!"
        if obj.__class__.__name__ != strType:
            raise ConceptNetworkBadType,"Not a "+strType+"!"

    def getNode(self,symbol):
        "Get the node from the concept network whose symbol is given"
        try:
            return self.node[symbol]
        except:
            raise ConceptNetworkUnknownNode,"Unknown node: \"" + symbol + "\""

    def addNode(self,node):
        "Add a Node to the Concept Network"
        self.__hasType(node,"Node")
        if node.getSymbol() in self.node:
            self.node[node.getSymbol()].incrementOcc()
        else:
            self.node[node.getSymbol()] = node

    def getLink(self,nodeFrom,nodeTo,nodeLabel=None):
        "Get the link going from nodeFrom to nodeTo, through nodeLabel (if it exists)"
        if not nodeFrom or not nodeTo:
            raise ConceptNetworkIncompleteLink,"There lacks at least one node!"
        self.__hasType(nodeFrom,"Node")
        self.__hasType(nodeTo,  "Node")
        if nodeLabel:
            self.__hasType(nodeLabel,"Node")
        return self.link[(nodeFrom,nodeTo,nodeLabel)]

    def getLinksFrom(self,nodeFrom):
        "Get links that go from nodeFrom"
        self.__hasType(nodeFrom,"Node")
        return [self.link[link] for link in self.link if link[0] == nodeFrom]

    def getLinksLabeled(self,nodeLabel):
        "Get links that go through nodeLabel, or from this node"
        self.__hasType(nodeLabel,"Node")
        return [self.link[link] for link in self.link if link[2] == nodeLabel]

    def getLinksLabeledOrTo(self,nodeLabel):
        "Get links that go through nodeLabel, or to this node."
        self.__hasType(nodeLabel,"Node")
        return [self.link[link] for link in self.link
                if link[2] == nodeLabel or link[1] == nodeLabel]

    def getLinksTo(self,nodeTo):
        """Get links clone that go to @a nodeTo.
           Don't get the !part_of! links."""
        self.__hasType(nodeTo,"Node")
        return [self.link[link] for link in self.link if link[1] == nodeTo]

    def addLink(self,nodeFrom, nodeTo, nodeLabel=None):
        """Add a directional link to the ConceptNetwork.

        If the link already exists, its co-occurrence is incremented.
        If there is no label node, None should be passed as labelNode."""
        if not nodeFrom or not nodeTo:
            raise ConceptNetworkIncompleteLink,"There lacks at least one node!"
        self.__hasType(nodeFrom,"Node")
        self.__hasType(nodeTo,  "Node")
        if nodeLabel:
            self.__hasType(nodeLabel,"Node")
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

        for symbol, node in self.node.iteritems():
            influence   = 0
            nbIncomings = 0
            newAv       = 0
            nodeState   = state.getNodeStateBySymbol(symbol)
            oldAV       = nodeState.getOldActivationValue()
            age         = nodeState.getAge()
            type        = node.getType()
            occ         = node.getOcc()
            links       = self.getLinksTo(node)
            # Compute the influence coming to the node
            for link in links:
                fromSymbol  = link.getNodeFrom().getSymbol()
                fromState   = state.getNodeStateBySymbol(fromSymbol)
                fromAV      = fromState.getOldActivationValue()
                weight      = link.getWeight(state)
                influence  += fromAV * weight
                nbIncomings+= 1
            #Compute the new activation value of the node
            influence   /= log(normalNumberComingLinks + nbIncomings) \
                         / log(normalNumberComingLinks)
            decay       = type.getDecay()
            minusAge    = 200 / (1+exp(-age / memoryPerf)) - 100
            newAV   = oldAV - decay * oldAV / 100 + influence - minusAge
            if newAV > 100: newAV = 100
            if newAV < 0:   newAV = 0
            nodeState.setActivationValue(newAV)

    def fastPropagateActivations(self,state,
                                 normalNumberComingLinks,
                                 memoryPerf = 80):
        """Propagates activation values within state.

        Propagates activation values within state (faster than
        propagateActivations).

        state: in which activation values are found and changed
        normalNumberComingLinks "normal" number of links for the
                            whole influence to be taken into account
        memoryPerf: memory performance (the higher, the better)"""
        influenceValues = {}
        influenceNb     = {}
        for symbol, nodeState in state.nodeState.iteritems():
            nodeState.ageActivationValues()

        ## Fill influence table ##
        # Get the nodes influenced by others
        for symbol, node in self.node.iteritems():
#            symbol  = node.getSymbol()
            if symbol:
                ov  = state.getNodeOldActivationValue(symbol)
                links = self.getLinksFrom(node)
                for link in links:
                    weight     = link.getWeight(state)
                    nodeTo     = link.getNodeTo()
                    linkSymbol = nodeTo.getSymbol()
                    inflNb     = linkSymbol in influenceNb and \
                                 influenceNb[linkSymbol] or 0
                    infl       = linkSymbol in influenceValues and \
                                 influenceValues[linkSymbol] or 0
                    infl      += 0.5 + ov * weight
                    influenceValues[linkSymbol] = infl
                    influenceNb[linkSymbol]     = (linkSymbol in influenceNb and
                                                   influenceNb[linkSymbol] or 0) \
                                                   + 1

        ## For all influenced nodes ##
        for symbol in influenceValues.keys():
            nodeState   = state.getNodeStateBySymbol(symbol)
            node        = self.getNode(symbol)
            influence   = influenceValues[symbol]
            nbIncomings = influenceNb[symbol]
            nodeType    = node.getType()
            decay       = nodeType.getDecay()
            newAV       = 0
            oldAV       = state.getNodeOldActivationValue(symbol)
            age         = nodeState.getAge()

            influence  /= log(normalNumberComingLinks + nbIncomings)\
                          / log(normalNumberComingLinks)
            minusAge    = 200 / (1 + exp(-age / memoryPerf)) - 100

            newAV       = oldAV - decay * oldAV / 100 + influence \
                          - minusAge
            if newAV > 100: newAV = 100
            if newAV < 0:   newAV = 0
            nodeState.setActivationValue(newAV)

    def dump(self,file,protocol=2):
        """Dump the Concept Network in the file

        File must be opened. File is not closed by the method."""
        pickle.dump(self,file,protocol)

class Node:
    """A ConceptNetworkNode is

    <n occ="13"     Occurrence
      t="token"    Type
      b="1"        Beginning of sentence
      m="12"       Middle of sentence
      e="1"        Ending of sentence
      >
     contenu
    </n>

    see ConceptNetwork.addNode"""
    def __init__(self, symbol, nodeType, occ=1):
        self.symbol = symbol
        self.setType(nodeType)
        self.occ = occ

    def incrementOcc(self):
        self.occ = self.occ + 1

    def getType(self):
        return self.__type

    def setType(self,nodeType):
        if nodeType.__class__.__name__ != 'NodeType':
            raise ConceptNetworkNodeTypeError, "Type is not a type!"
        self.__type = nodeType

    def getSymbol(self):
        "Get the symbol of the node"
        return self.symbol

    def getOcc(self):
        return self.occ

class NodeType:
    """   A ConceptNetworkType is a @c t XmlNode

    TODO: REWRITE!
    @code
    <types>
    <t desac="50">sentence</t>
    <t desac="40">token</t>
    <t desac="40">expression</t>
    <t desac="10">sentiment</t>
    <t desac="70">utterer</t>
    <t desac="10">label</t>
    <t desac="50">file</t>
    </types>
    @endcode

    - @a desac is the decay rate.
    - @a depth is the depth of type
    - @a contents is the name of the type.

    The different types:
    - sentence (something said by someone, delimited by
      E_SENTENCE_SEPARATORS)
    - token (something inside a sentence)
    - expression (a sequence of tokens, often occurring - more than
      E_EXPRESSION_THRESHOLD)
    - sentiment
    - utterer (someone that said something, may it be a bot)
    - label (something linking two tokens or expressions). Changes the
      influence from one to another.
    - file (an URI, a file read).

    @see XmlNode ConceptNetworkCreate ConceptNetworkTypeGetDepth"""
    possibleTypes = {"sentence"   : 50,
                     "token"      : 40,
                     "expression" : 40,
                     "sentiment"  : 10,
                     "utterer"    : 70,
                     "label"      : 10,
                     "file"       : 50,
                     }
    def __init__(self,name,depth=50):
        if name in self.__class__.possibleTypes:
            self.name  = name
            self.depth = depth
            self.decay = self.__class__.possibleTypes[name]
        else:
            raise ConceptNetworkNodeTypeError, "Unknown node type:\"" + name + "\""

    def getDepth(self):
        return self.depth

    def getDecay(self):
        "Get the decay rate of the type"
        return self.decay

    def getName(self):
        "Get the name of that type"
        return self.name

class Link:
    """Type of the a Concept Network node

    A ConceptNetworkLink
    @code
    <l f="fromSymbol"   Incoming node (identified by its symbol)
      t="toSymbol"     Outgoing node (identified by its symbol)
      l="labelSymbol"  Label node (optional, identified by its symbol)
      co="2"           Co-occurrences of f and t.
    >
    @endcode

    @see XmlNode ConceptNetworkAddLink
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
        weight  = self.coOcc / occ
        if self.label:
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
    """   A ConceptNetworkState is an XmlNode.

    It is attached to an ECTOR's user.

    The name of the user should be the name of the file in which the
    ConceptNetworkState is saved.

    @code
    <state user="H_I">
     <n age="2" av="100" ov="0" >nodeSymbol</n>
     <n age="0" av="10"  ov="12">nodeSymbol2</n>
     <n age="10" av="7"  ov="0" >nodeSymbol3</n>
     ...
     <n age="2" av="54"  ov="56">nodeSymbolN</n>
     <sentence>
       <n>How</n>
       <n>are</n>
       <n>you</n>
       <n>?</n>
     </sentence>
    </state>
    @endcode

    Each node in the state has:
    - a symbol (which identifies it in the ConceptNetwork)
    - an @a age (which is the number of propagation since the last
     complete activation of the node)
    - an @a av <b>a</b>ctivation <b>v</b>alue
    - an @a ov <b>o</b>ld activation <b>v</b>alue


    The @a sentence part is not required. It contains one or more nodes of
    the ConceptNetwork @see ConceptNetwork, that one can link to the next
    entry of the user."""
    def __init__(self,stateId):
        self.id        = stateId
        self.nodeState = {}         # node symbol -> node state

    def getNodeStateBySymbol(self,symbol):
        """Get the the state of the node which symbol is given.

        If the state did not exist, it is created with default arguments."""
#        print "****** getNodeStateBySymbol(%s)" % symbol
#        print "nodeState[].keys:"
#        for k in self.nodeState.keys():
#            print "\t%s" % k

        if symbol not in self.nodeState:
#            print "\tNot in nodeState[]"
            self.nodeState[symbol] = NodeState()
#            print repr(self.nodeState[symbol].activationValue)
        self.checkNodes()
        return self.nodeState[symbol]

    def setNodeActivationValue(self,symbol, activationValue):
        """Set the activationValue to the node which symbol is given in Concept Network State."""
        nodeState = self.getNodeStateBySymbol(symbol)
        self.__hasType(nodeState,"NodeState")
        if activationValue:
            nodeState.setActivationValue(activationValue)
        else:
            # If it is deleted, the age is no more known
            age = nodeState.age
            if age > 50:
                self.nodeState.pop(symbol)

    def getNodeActivationValue(self,symbol):
        """Get the activationValue of the node which symbol is given from Concept Network State."""
        nodeState = self.getNodeStateBySymbol(symbol)
        if nodeState.__class__.__name__ != "NodeState":
            raise ConceptNetworkStateBadType, \
                "The state of \""+symbol+"\" is not a NodeState!"
        return nodeState.getActivationValue()

    def getNodeOldActivationValue(self,symbol):
        """Get the old activationValue of the node which symbol is given from Concept Network State."""
        nodeState = self.getNodeStateBySymbol(symbol)
        return nodeState.getOldActivationValue()

    def setInfluence(self,symbol, influence):
        """Set the influence to the node which symbol is @a nodSymbol in cns."""
        nodeState = self.getNodeStateBySymbol(symbol)
        nodeState.setInfluence(influence)

    def getInfluence(self,symbol, influence):
        """Set the influence to the node which symbol is @a nodSymbol in cns."""
        nodeState = self.getNodeStateBySymbol(symbol)
        return nodeState.getInfluence()

    def getAverageActivationValue(self):
        "Get the average activation value"
        activationValues = [nodeState.getActivationValue()
                            for symbol, nodeState in self.nodeState.iteritems()]
        nb  = len(activationValues)
        sum = sum(activationValues)
        if nb:  return sum / nb
        else:   return 0

    def getMaximumActivationValue(self, cn, typeNames):
        """Get the maximum activation value of the state, within nodes of types given by typeNames

        typeNames: names of the types to take into account
        cn:        Concept Network containing the nodes"""
        activationValues = [nodeState.getActivationValue()
                            for symbol, nodeState in self.nodeState.iteritems()
                            if ConceptNetwork.getNode(nodeState.getSymbol()).getType().getName() in typeNames]
        return max(activationValues)

    def getActivatedTypedNodes(self, cn, typeNames, threshold=90):
        """Get the activated nodes of cn.

        The returned nodes must be in the list of typeNames, and
        have an activation value greater than threshold

        Return a list of tuples (node,activation value)"""
        nodes = []
        for symbol, node in cn.node.iteritems() :
            symbol  = node.getSymbol()
            av      = self.getNodeActivationValue(symbol)
            if av > threshold:
                if node.getType().getName() in typeNames:
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
        for symbol, nodeState in self.nodeState.iteritems():
            self.__hasType(nodeState,"NodeState")

    def showNodes(self):
        "Print the node states"
        print "Symbol\t\toldav\tav\tage"
        for symbol in self.nodeState:
            nodeState = self.nodeState[symbol]
            print "state(%s):\t%s\t%d\t%d" % (symbol,
                                              nodeState.getOldActivationValue(),
                                              nodeState.getActivationValue(),
                                              nodeState.getAge())

class NodeState:
    """The state of a node (activation value, old activation value, age)"""
    def __init__(self, activationValue=0, age=0):
        self.oldActivationValue = 0
        self.activationValue    = activationValue
        self.age                = age
        self.influence          = 0

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

    def setInfluence(self,influence):
        """Set the influence to the node.

        Influence represents the sum of the activation values coming
        in the node"""
        self.influence = influence

    def getInfluence(self):
        return self.influence

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

if __name__ == "__main__":
    # Default encoding for UTF-8
    import sys
    #sys.setdefaultencoding('iso−8859−1')

    conceptNetwork = ConceptNetwork()
    nodeFrom = Node("From",NodeType("token"))
    nodeTo1  = Node("To1", NodeType("token"))
    conceptNetwork.addNode(nodeFrom)
    conceptNetwork.addNode(nodeTo1)
    conceptNetwork.addLink(nodeFrom, nodeTo1)
    state = State(1)
    conceptNetwork.addState(state)
    state.checkNodes()
    state.setNodeActivationValue("From",100)
    state.checkNodes()
    conceptNetwork.fastPropagateActivations(state,2)
    state.showNodes()
    print "To1: %d" % state.getNodeActivationValue("To1")

    f = open("cn.data","w")
    conceptNetwork.dump(f,0)

    sys.exit(0)
    cn    = ConceptNetwork()
    TOKEN = NodeType("token")
    node1 = Node("Salut",TOKEN)
    node2 = Node("toi",TOKEN)
    cn.addLink(node1,node2)
    print "getLinksFrom(\"Salut\")"
    print cn.getLinksFrom(node1)

    l = [(node1,59),(node2,41)]
    temperature = Temperature(55)
    temperature.randomize()

    print temperature.chooseWeightedItem(l).getSymbol()
