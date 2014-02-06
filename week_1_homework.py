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




            
        







