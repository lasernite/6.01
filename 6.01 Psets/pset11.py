import lib601.dist as dist
from lib601.dist import *

def independentJoint(pX,pY):
    return makeJointDistribution(pX,pY)


def test():
    one = dist.DDist({1: 0.005647717714630461, 2: 0.9416434472677528, -1: 0.052708835017616695})
    two = dist.DDist({0: 0.8488172888133854, 2: 0.07020395977467608, -1: 0.0009530382994862124, -2: 0.08002571311245232})
    ans = independentJoint(one,two).d
    return ans
