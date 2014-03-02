from lib601.sm import SM

class LTISM (SM):
    def __init__(self, dCoeffs, cCoeffs):
        self.cCoeffs = cCoeffs #output
        self.dCoeffs = dCoeffs #input

        #replace the starting state if necessary
        self.startState = [[0]*len(dCoeffs),[0]*len(cCoeffs)]

    def getNextValues(self, state, inp):
        xs = sum([state[0][i]*self.dCoeffs[i+1] for i in range(len(self.dCoeffs)-1)])
        ys = sum([state[1][i]*self.cCoeffs[i] for i in range(len(self.cCoeffs))])
        if len(self.dCoeffs) == 0:
            output = xs + ys
        else:
            output = inp*self.dCoeffs[0] + xs + ys
        nextState = [[inp] + state[0], [output] + state[1]]
        return (nextState, output)


''' components

print "x[n]: ", inp*self.dCoeffs[0], "x[n-1]: ", state[0][0]*self.dCoeffs[0]
        print "y[n-1]: ", state[1][0]*self.cCoeffs[0], "y[n-2]: ", state[1][1]*self.cCoeffs[1]

'''


