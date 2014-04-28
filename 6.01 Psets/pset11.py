import lib601.dist as dist
from lib601.dist import *

def independentJoint(pX,pY):
    return makeJointDistribution(pX, lambda x: pY)
    
def testij():
    one = dist.DDist({0: 0.969039238735483, -1: 0.006066412376441344, -2: 0.024894348888075638})
    two = dist.DDist({0: 0.5494404802642207, 1: 0.18777777160787765, -2: 0.24123359568494385, -1: 0.021548152442957845})
    ans = independentJoint(one,two).d
    return ans

def independentSum(pA, pB):
    inde = independentJoint(pA,pB)
    return inde.project(lambda tpl: tpl[0] + tpl[1])
    
def testis():
    one = dist.DDist({0: 0.21486219836484893, 1: 0.2327604265544868, 2: 0.033968814709159384, -2: 0.5184085603715048})
    two = dist.DDist({1: 0.8545818193834935, -1: 0.14541818061650646})
    ans = independentSum(one,two).d
    return ans

# 0.5, 0.666, 0.333
Car = DDist({1:1./3, 2:1./3, 3:1./3})
Select = DDist({1:1./3, 2:1./3, 3:1./3})
totalUnselected = lambda (C,S): sum([1 for door in range(1,4) if (door != C and door != S)])
HostGivenCarAndSelect = lambda (C,S): DDist({door: 1./totalUnselected( (C,S) ) if (door != C and door != S) else 0 for door in range(1,4)})

PCSH = makeJointDistribution(independentJoint(Car, Select), HostGivenCarAndSelect)
PCS1H = PCSH.condition(lambda ((c,s),h): s == 1)
PCS1H = PCS1H.project(lambda ((c,s),h): h)
pH3GivenS1 = PCS1H.prob(3)


PCH3S1 = PCSH.condition(lambda ((c,s),h): s == 1 and h == 3)
PCH3S1 = PCH3S1.project(lambda ((c,s),h): c)
pC2GivenH3S1 = PCH3S1.prob(2)

pC1GivenH3S1 = Car.prob(1)


def squareDist(lo, hi, loLimit = None, hiLimit = None):
    d = {key:1.0/(hi-lo) for key in range(lo,hi)}
    dilim = {}
    for key in d:
        if key <= loLimit:
            if loLimit in dilim:
                dilim[loLimit] += d[key]
            else:
                dilim[loLimit] = d[key]
        elif key >= hiLimit and hiLimit != None:
            if hiLimit in dilim:
                dilim[hiLimit] += d[key]
            else:
                dilim[hiLimit] = d[key]
        else:
            dilim[key] = d[key]          
    return dist.DDist(dilim)


def triangleDist(peak, halfWidth, loLimit = None, hiLimit = None):
    pass # your code here
