class UserFunctionIF():
    def __init__(self):
        self.fn = {'setup': [],
                   'brainStart': [],
                   'step': [],
                   'brainStop': [],
                   'shutdown': []}

    def registerFn(self, type, f):
        self.fn[type].append(f)

    def callFunctions(self, type):
        for f in self.fn[type]:
            f()

    def clearFunctions(self):
        for k in self.fn.keys():
            self.fn[k] = []
            

    
