from lib601.sm import *

class CommentsSM(SM):
    startState = 'not_comment'

    def getNextValues(self, state, inp):
        if inp in ("\n", "#"):
            if state == "comment":
                output = None
                nextState = "not_comment"
            else:
                output = inp
                nextState = "comment"
        else:
            if state == "comment":
                output = inp
                nextState = "comment"
            else:
                output = None
                nextState = "not_comment"

        return (nextState, output)



class RibosomeSM(SM):
    def __init__(self):
        self.startState = ['notORF', [] ]
        self.rnatoAminoAcid = {"UUU":"Phenylalanine", "UUC":"Phenylalanine", "UUA":"Leucine", 
    "UCU":"Serine", "UCC":"Serine", "UCA":"Serine", "UCG":"Serine",
    "UAU":"Tyrosine", "UAC":"Tyrosine", "UAA":"STOP", "UAG":"STOP",
    "UGU":"Cysteine", "UGC":"Cysteine", "UGA":"STOP", "UGG":"Tryptophan",
    "CUU":"Leucine", "CUC":"Leucine", "CUA":"Leucine", "CUG":"Leucine",
    "CCU":"Proline", "CCC":"Proline", "CCA":"Proline", "CCG":"Proline",
    "CAU":"Histidine", "CAC":"Histidine", "CAA":"Glutamine", "CAG":"Glutamine",
    "CGU":"Arginine", "CGC":"Arginine", "CGA":"Arginine", "CGG":"Arginine",
    "AUU":"Isoleucine", "AUC":"Isoleucine", "AUA":"Isoleucine", "AUG":"Methionine",
    "ACU":"Threonine", "ACC":"Threonine", "ACA":"Threonine", "ACG":"Threonine",
    "AAU":"Asparagine", "AAC":"Asparagine", "AAA":"Lysine", "AAG":"Lysine",
    "AGU":"Serine", "AGC":"Serine", "AGA":"Arginine", "AGG":"Arginine",
    "GUU":"Valine", "GUC":"Valine", "GUA":"Valine", "GUG":"Valine",
    "GCU":"Alanine", "GCC":"Alanine", "GCA":"Alanine", "GCG":"Alanine",
    "GAU":"Aspartic Acid", "GAC":"Aspartic Acid", "GAA":"Glutamic Acid", 
    "GAG":"Glutamic Acid", "UUG":"Leucine",
    "GGU":"Glycine", "GGC":"Glycine", "GGA":"Glycine", "GGG":"Glycine",}

    def getNextValues(self,state,inp):
        # If last three letters read is AUG, ORF Start
        if "".join(state[1][-3:]) == 'AUG' and state[0] == "notORF":
            nextState = ['ORF', [inp]]
            output = self.rnatoAminoAcid['AUG']
        # Else still notORF, append input to state
        elif state[0] == "notORF":
            state[1].append(inp)
            nextState = ['notORF', state[1]]
            output = None

        # If State is ORF, begin reading
        elif state[0] == 'ORF':
            # If three letters read, return protein or None and change state
            if len(state[1]) == 3:
                seq = "".join(state[1])
                # If stop codon
                if self.rnatoAminoAcid[seq] == "STOP":
                    output = None
                    nextState = ['notORF', []]
                # Else protein
                else:
                    output = self.rnatoAminoAcid[seq]
                    nextState = ['ORF',[inp]]
                    
            # Else return None and incomplete read
            else:
                output = None
                state[1].append(inp)
                nextState = ['ORF', state[1]]

        return [nextState, output]


class Polynomial:
    ## Intialize a polynomial with a list of coefficients.
    ## The coefficient list starts with the highest order term.
    def __init__(self, coeffs):
        self.coeffs = coeffs
        self.order = len(self.coeffs) - 1

    ## Return the coefficient of the x**i term
    def coeff(self,i):
        return self.coeffs[-i-1]

    ## Return the value of this Polynomial evaluated at x=v
    def val(self, v):
        value = 0
        for powi in range(len(self.coeffs)):
            value += self.coeffs[-(powi+1)] * v**powi
        return value

    ## Return the roots of this Polynomial
    def roots(self):
        if len(self.coeffs) > 3:
            return "Don't handle polynomials of order greater than 2"
        elif len(self.coeffs) == 3:
            if (self.coeffs[1]**2)-(4*self.coeffs[0]*self.coeffs[2]) < 0:
                a = (((self.coeffs[1]**2)-(4*self.coeffs[0]*self.coeffs[2])) * -1) **0.5
                return (complex((-self.coeffs[1])/(2*self.coeffs[0]),a/(2*self.coeffs[0])), complex((-self.coeffs[1])/(2*self.coeffs[0]),-a/(2*self.coeffs[0])))
            else: 
                root1 = ((-self.coeffs[1]) + ((self.coeffs[1]**2)-(4*self.coeffs[0]*self.coeffs[2]))**0.5)/(2*self.coeffs[0])
                root2 = ((-self.coeffs[1]) - ((self.coeffs[1]**2)-(4*self.coeffs[0]*self.coeffs[2]))**0.5)/(2*self.coeffs[0])
                if root1 == root2:
                    return [root1]
                else:
                    return [root1,root2]
            
        elif len(self.coeffs) == 2:
            return (-self.coeffs[1])/self.coeffs[0]
        elif len(self.coeffs) == 1:
            return None
        else:
            return None
            
        
    ## Add two polynomials, return a new Polynomial
    def add (self, other):
        if len(self.coeffs) >= len(other.coeffs):
            new_poly = Polynomial(list(self.coeffs))
            for i in range(1,len(other.coeffs)+1):
                new_poly.coeffs[-i] += other.coeffs[-i]
            return new_poly
        else:
            new_poly = Polynomial(list(other.coeffs))
            for i in range(1,len(self.coeffs)+1):
                new_poly.coeffs[-i] += self.coeffs[-i]
            return new_poly

    
    ## Multiply two polynomials, return a new Polynomial
    def mul(self, other):
        oc = other.coeffs
        sc = self.coeffs
        total = Polynomial([])
        alist = []

        for i in range(len(oc)):
            for a in range(len(sc)):
                alist.append(oc[-i-1]*sc[a])
            alist += [0] * i
            new = Polynomial(list(alist))
            total += new
            alist = []
        return total
    
   
    '''
if len(self.coeffs) >= len(other.coeffs):
            new_poly = Polynomial(list(self.coeffs))
            for i in range(1,len(other.coeffs)+1):
                new_poly.coeffs[-i] *= other.coeffs[-i]
            return new_poly
        else:
            new_poly = Polynomial(list(other.coeffs))
            # for index of the coefficents, and powers (backwards)
            for i in range(1,len(self.coeffs)+1):
                # multiply each item by every in list and add power as zeros
                new_list = []
                for n in range(1,len(self.coeffs)+1):
                    new_list = 
                # create expansion (multiply first by whole)
                new_poly.coeffs[-i] *= self.coeffs[-i]
                # add expansions together
                total += 
            return new_poly
    '''


    def __add__(self, other):
        #override the + operator so we can do things like p1+p2
        return self.add(other)

    def __mul__(self, other):
        #override the * operator so we can do things like p1*p2
        return self.mul(other)

    def __str__(self):
        coeffs = self.coeffs
        return 'Polynomial(%r)' % coeffs

def testpolyadd():
    a = Polynomial([1, -7, 10, -4, 6])
    b = Polynomial([1,1,1,1,1,1,1,1])
    print (a+b).coeffs
    print a.coeffs
    print b.coeffs
    

def testpolyaddrev():
    a = Polynomial([1,1,1,1,1,1,1,1])
    b = Polynomial([1, -7, 10, -4, 6])
    print (a+b).coeffs
    print a.coeffs
    print b.coeffs

def testpolymul():
    a = Polynomial([1,2])
    b = Polynomial([2,1])
    print a.coeffs
    print b.coeffs
    print (a*b).coeffs

def testpolymulrev():
    a = Polynomial([6,4,2,0,2,4])
    b = Polynomial([2,3,5,7])
    print (a*b).coeffs
    print a.coeffs
    print b.coeffs

def testpolym():
    p1 = Polynomial([0.18909394898655085, 0.6572217572022152, 0.8843518945016113])
    p2 = Polynomial([0.8938517060972571, 0.2755190448329632, 0.19911524675579406, 0.7474832756354785, 0.08532799082773201])
    a = p1.mul(p2)
    ans = ["%.03f" % a.coeff(i) for i in xrange(a.order+1)]
    print ans

a = Polynomial([1,2,3,4])
b = Polynomial([4,3,2,1])

   
        
        
            

