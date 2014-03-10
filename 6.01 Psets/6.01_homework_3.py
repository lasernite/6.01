from lib601.poly import *

class SystemFunctional:
    def __init__(self, numerator, denominator):
        self.numerator = numerator
        self.denominator = denominator

    def poles(self):
        x = [n for n in reversed(self.denominator.coeffs)]
        m = Polynomial(x)
        return m.roots()
                
    def poleMagnitudes(self):
        return [abs(p) for p in self.poles()]

    def dominantPole(self):
        if self.poleMagnitudes()[0] > self.poleMagnitudes()[1]:
            return self.poles()[0]
        else:
            return self.poles()[1]


######################################################################
##    Primitive SFs
######################################################################

def Gain(k):
    return SystemFunctional(Polynomial([k]),Polynomial([1]))

def R():
    return SystemFunctional(Polynomial([1,0]),Polynomial([1]))


######################################################################
# Combining SFs
######################################################################

def Cascade(sf1, sf2):
    numer = sf1.numerator * sf2.numerator
    denom = sf1.denominator * sf2.denominator
    return SystemFunctional(numer, denom)

def testcas():
    a = Polynomial([1,2,3])
    b = Polynomial([3,2,1])
    c = Polynomial([3,3,3])
    d = Polynomial([2,1,2])
    e = SystemFunctional(a,b)
    f = SystemFunctional(c,d)
    print Cascade(e,f).numerator, Cascade(e,f).denominator

def FeedbackAdd(sf1, sf2):
    numer = sf1.numerator*sf2.denominator
    denom = (sf1.denominator*sf2.denominator) - (sf1.numerator*sf2.numerator)
    return SystemFunctional(numer, denom)

def test1():
    a = Gain(7.261984)
    b=R()
    return FeedbackAdd(a,b)

def test2():
    a = Gain(4.470611)
    b=R()
    return FeedbackAdd(b,a)

def test3():
    a = Gain(-1.318422)
    b=R()
    return FeedbackAdd(Cascade(a,b),b)

def test4():
    a = Gain(5.739113)
    b=R()
    return FeedbackAdd(b,FeedbackAdd(a,b))

def test5():
    a = Gain(-2.685104)
    b=R()
    return FeedbackAdd(FeedbackAdd(a,b),FeedbackAdd(b,a))


    
