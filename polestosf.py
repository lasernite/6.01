import lib601.poly as poly
import lib601.sf as sf

def polesToSF(poles):
    numpoly = poly.Polynomial([1])
    denompoly = poly.Polynomial([1])
    for pole in poles:
        polePoly = poly.Polynomial([1,-pole])
        denompoly = denompoly * polePoly

    denomlist = [x for x in reversed(denompoly.coeffs)]

    denomp = poly.Polynomial(denomlist)

    return sf.SystemFunctional(numpoly,denomp)
