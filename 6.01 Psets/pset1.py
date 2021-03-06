def isPalindrome(x):
    return x[::-1] == x

def isSubstring(a,b):
    return a in b

def extractTags(s):
    tags_list = []
    if '[' and ']' not in s:
        return tags_list
    while len(s) > 1:
        start = 0
        end = 0
        while s[start] != '[':
            start += 1
        while s[end] != ']':
            end += 1
        tags_list.append(s[start+1:end])
        s = s[end+1:]
    return tags_list
                
c = [[[4]],[1],[2,[-5]],-2]

a = [1,2,3]
b = [a,a]

a = [3,[1,2]]
b = a

class FruitSalad:
    fruits = ['melons', 'pineapples']
    servings = 4

    def __init__(self, ingredients, numServings): # must supply self as first parameter 
        self.fruits = ingredients
        self.servings = numServings

    def __str__(self):
        return str(self.servings) + " servings of fruit salad with " + str(self.fruits)

    def add( self, ingredient ):
        self.fruits.append(ingredient)

    def serve( self ):
        if self.servings >= 1:
            self.servings += -1
            return 'enjoy'
        else:
            return 'sorry'


def warehouseProcess(warehouseStuff, transaction):
    if transaction[0] == 'receive' and transaction[1] not in warehouseStuff.keys():
        warehouseStuff[transaction[1]] = transaction[2]
    elif transaction[0] == 'receive' and transaction[1] in warehouseStuff.keys():
        warehouseStuff[transaction[1]] += transaction[2]
    elif transaction[0] == 'ship' and transaction[1] in warehouseStuff.keys():
        warehouseStuff[transaction[1]] -= transaction[2]
    else:
        return 'something went wrong'



class Warehouse():
    
    def __init__(self):
        self.warehouseStuff = {}

    def process(self, transaction):
        (operation, item, amount) = transaction
        if operation == 'receive' and item not in self.warehouseStuff.keys():
            self.warehouseStuff[item] = amount
        elif operation == 'receive' and item in self.warehouseStuff.keys():
            self.warehouseStuff[item] += amount
        elif operation == 'ship' and item in self.warehouseStuff.keys():
            self.warehouseStuff[item] -= amount
        else:
            return 'Something in processing went wrong.'

    def lookup(self, item):
        if item in self.warehouseStuff.keys():
            return self.warehouseStuff[item]
        else:
            return 0

def evenSquares(numbers):
    return [x**2 for x in numbers if x % 2 == 0]

''' def sumAbsProd(a,b):
    numbers = []
    for anum in range(len(a)):
        for bnum in range(len(b)):
            numbers.append(abs(a[anum])*abs(b[bnum])) 
    return sum([x for x in numbers]) '''

def sumAbsProd(list1,list2):
    multiplied_list = [abs(x*y) for x in list1 for y in list2]
    return sum(multiplied_list)
        

from lib601.sm import *

class Delay(SM):
    def __init__(self):
        self.startState = 0
    def getNextValues(self, state, inp):
        nextState = inp
        output = state
        return (nextState,output)


class DoubleDelay(SM):
    def __init__(self):
        self.startState = (0 , 0)
    def getNextValues(self, state, inp):
        nextState = (inp, state[0])
        output = state[1]
        return (nextState,output)


class DelayN(SM):
    def __init__(self, n):
        self.startState = [0] * n
    def getNextValues(self, state, inp):
        output = state[0]
        nextState = state[1:]
        nextState.append(inp)
        return (nextState,output)

class Fib(SM):
    def __init__(self):
        self.startState = [0, 1]
    def getNextValues(self, state, inp):
        if state == self.startState:
            output = 0
            nextState = [0]
            return (nextState,output)
        elif state == [0]:
            output = 1
            nextState = [1,0]
            return (nextState,output)
        elif state == [1,0]:
            output = 1
            nextState = [1,1]
            return (nextState,output)
        else:
            output = state[0] + state[1]
            nextState = [state[1]]
            nextState.append(output)
            return (nextState,output)

''' More efficient

class Fib(SM):
    startState = (0,1)

    def getNextValues(self, state, inp):
        x, y = state
        nextState = (y, x+y)
        out = x
        return (nextState, out)

        '''

def fib(n):
    all_fib = []
    if n == 0:
        return 0
    elif n == 1:
        return 1
    for x in range(n+1):
        if x == 0:
            all_fib.append(0)
        elif x == 1:
            all_fib.append(1)
        else:
            all_fib.append(all_fib[x-1] + all_fib[x-2])
    return all_fib[n]


def lc(f, g, items):
   return [f(x) for x in items if g(x)]


def oddx100(stuff):
    def f(x):
        return x*100
    def g(x):
        return x % 2 == 1
    return lc(f,g,stuff)

def flub(stuff):
    return lc(lambda x: x + 'ubblefub', lambda x: type(x) == str, stuff)


# Vectors
class V2:
    
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def add(self, v):
        x = self.x + v.x
        y = self.y + v.y
        return V2(x, y)

    def mul(self, s):
        x = self.x * s
        y = self.y * s
        return V2(x,y)

    def __add__(self, v):
        return self.add(v)

    def __mul__(self, s):
        return self.mul(s)
    
    def __str__(self):
        return 'V2' + str([self.x, self.y])


# Symbolic Algebra

class Symbol:
    def __repr__(self):
        return self.__str__()
    # the following methods are special in Python, and 
    # allow us to manipulate symbols using Python's operators
    # + and *
    def __add__(self,other):
        return Add(self,other)
    def __mul__(self,other):
        return Mul(self,other)

class Var(Symbol):
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return "Var(" + repr(self.name) + ")"
    def isConst(self):
        return False
    def evaluate(self, bindings):
        return bindings[self.name]
    def deriv(self, v):
        if v == self.name:
            return Num(1)
        else:
            return Num(0)
        

class Num(Symbol):
    isConst = True
    def __init__(self, val):
        self.val = val
    def __str__(self):
        return "Num(" + repr(self.val) + ")"
    def isConst(self):
        return True
    def evaluate(self, bindings):
        return self.val
    def deriv(self,v):
        return Num(0)

class BinOp(Symbol):
    def __init__(self,left,right):
        self.left = left
        self.right = right
    def __str__(self):
        return "(" + str(self.left) + " " + self.op_str + " " + str(self.right) + ")"
    def isConst(self):
        return self.left.isConst() and self.right.isConst()
    def evalConst(self):
        return self.left.val + self.right.right.val * self.right.left.val
    def evaluate(self, bindings):
        return self.fun(self.left.evaluate(bindings), self.right.evaluate(bindings))
    

            
class Add(BinOp):
    op_str = "+"
    def fun(self, x, y):
        return x + y
    def deriv(self,v):
        return self.left.deriv(v) + self.right.deriv(v)
    
class Mul(BinOp):
    op_str = "*"
    def fun(self, x, y):
        return x * y
    def deriv(self, v):
        return self.left.deriv(v)*self.right + self.right.deriv(v)*self.left

def balance(deposit, years):
    return deposit*(1.05**years)




            
        







