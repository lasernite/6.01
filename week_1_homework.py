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
        

''' class Delay(SM):
    def __init__(self):
        self.startState = 0
    def getNextValues(self, state, inp):
        nextState = inp
        output = state
        return (nextState,output) '''


'''class DoubleDelay(SM):
    def __init__(self):
        self.startState = (0 , 0)
    def getNextValues(self, state, inp):
        nextState = (inp, state[0])
        output = state[1]
        return (nextState,output) '''


''' class DelayN(SM):
    def __init__(self, n):
        self.startState = [0] * n
        self.n = n
        #your code here
    def getNextValues(self, state, inp):
        nextState = [inp, state[0:self.n-2]]
        output = state[self.n-2]
        return (nextState,output) '''

def lc(f, g, items):
   return [f(x) for x in items if g(x)]


def oddx100(stuff):
    def f(x):
        return x*100
    def g(x):
        return x % 2 == 1
    return lc(f,g,stuff)


            
        







