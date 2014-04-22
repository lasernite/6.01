class SearchNode:
    def __init__(self, state, parent, cost = 0.):
        self.state = state
        self.parent = parent
    def path(self):
        p = []
        node = self
        while node:
            p.append(node.state)
            node = node.parent
        p.reverse()
        return p

class Stack:
    def __init__(self):
        self.data = []
    def push(self, item):
        self.data.append(item)
    def pop(self):
        return self.data.pop()
    def isEmpty(self):
        return len(self.data) == 0

class Queue:
    def __init__(self):
        self.data = []
    def push(self, item):
        self.data.append(item)
    def pop(self):
        return self.data.pop(0)
    def isEmpty(self):
        return len(self.data) == 0

def depthFirstSearch(successors, startState, goalTest):
    if goalTest(startState):
        return [startState]
    startNode = SearchNode(startState, None)
    agenda = Stack()
    agenda.push(startNode)
    while not agenda.isEmpty():
        parent = agenda.pop()
        newChildStates = [] #for pruning rule 2
        for childState in successors(parent.state):
            child = SearchNode(childState, parent)
            if goalTest(childState):
                return child.path()
            elif childState in newChildStates: #pruning rule 2
                pass
            elif childState in parent.path(): #pruning rule 1
                pass
            else:
                newChildStates.append(childState)
                agenda.push(child)
    return None

def breadthFirstSearch(successors, startState, goalTest):
    if goalTest(startState):
        return [startState]
    startNode = SearchNode(startState, None)
    agenda = Queue()
    agenda.push(startNode)
    visited = {startState} #initialize our visited set
    while not agenda.isEmpty():
        parent = agenda.pop()
        for childState in successors(parent.state):
            child = SearchNode(childState, parent)
            if goalTest(childState):
                return child.path()
            elif childState not in visited:
                visited.add(childState)
                agenda.push(child)
    return None

def search(successors, startState, goalTest, dfs=False):
    if dfs:
        return depthFirstSearch(successors, startState, goalTest)
    else:
        return breadthFirstSearch(successors, startState, goalTest)

def KnightSuccessor(state):
    moves = [(1,2),(1,-2),(-1,2),(-1,-2),(2,1),(2,-1),(-2,1),(-2,-1)]
    boardX, boardY = (8,8)
    out = []
    x,y = state
    for dx,dy in moves:
        nx,ny = x+dx,y+dy
        if (-1<nx<boardX) and (-1<ny<boardY):
            out.append((nx,ny))
    return out

def test():
    print len(search(KnightSuccessor,(0,0),lambda s: s==(7,7))), len(search(KnightSuccessor,(7,7),lambda s: s==(7,7)))


# Word Ladders

from string import *

WORDS = set([i.lower().strip() for i in open('words2.txt').readlines()])

def is_valid_word(word):
    return word in WORDS

def wordLadderSuccessor(word):
    valid = []
    for l_i in range(len(word)):
        for letter in ascii_lowercase:
            list_word = list(word)
            list_word[l_i] = letter
            list_word = ''.join(list_word)
            if is_valid_word(list_word):
                valid.append(list_word)
    return valid

''' This way is slow but works

def wordLadderSuccessor(word):
    valid = []
    for dic_word in WORDS:
        # Sameness Index
        same = 0
        # Compare dictionary words of same length
        if len(dic_word) == len(word):
            # Compare letters of words
            for i in range(len(word)):
                if dic_word[i] == word[i]:
                    same += 1
        if same + 1 == len(word):
            valid.append(dic_word)
    return valid
'''

# Flight Itinerary

def findItinerary(startCity, startTime, endCity, deadline):
    goalTest = lambda (city,time): city == endCity and time < deadline
    return search(flightSuccessors, (startCity,startTime), goalTest)

class Flight:
    def __init__(self, startCity, startTime, endCity, endTime):
        self.startCity = startCity
        self.startTime = startTime
        self.endCity = endCity
        self.endTime = endTime

    def matches(self, (city, time)):
        return self.startCity == city and time < self.startTime

    def __str__(self):
        return str((self.startCity, self.startTime))+' -> '+ str((self.endCity, self.endTime))
    __repr__ = __str__

def flightSuccessors(state):
    nextstates = []
    for flight in flightDB:
        if flight.matches(state):
            nextstates.append((flight.endCity,flight.endTime))
    return nextstates

def findShortestItinerary(startLoc, endLoc):
    startd = 1
    currentd = startd - 1
    nex = None

    while nex == None:
        currentd += 1
        nex = findItinerary(startLoc, startd, endLoc, currentd)
    return nex



