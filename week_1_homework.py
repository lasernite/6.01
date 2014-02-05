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






