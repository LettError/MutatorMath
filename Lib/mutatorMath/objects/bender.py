
import sys
from mutatorMath.objects.error import MutatorError
from mutatorMath.objects.location import Location, biasFromLocations
import mutatorMath.objects.mutator

def noBend(loc): return loc

class WarpMutator(mutatorMath.objects.mutator.Mutator):
    def __call__(self, value):
        return self.makeInstance(Location(w=value))

"""

    A warpmap is a list of tuples that describe non-linear behaviour
    for a single dimension in a designspace.

    Bender is an object that accepts warpmaps and transforms
    locations accordingly.

    For instance:
        w = {'a': [(0, 0), (500, 200), (1000, 1000)]}
        b = Bender(w)
        assert b(Location(a=0)) == Location(a=0)
        assert b(Location(a=250)) == Location(a=100)
        assert b(Location(a=500)) == Location(a=200)
        assert b(Location(a=750)) == Location(a=600)
        assert b(Location(a=1000)) == Location(a=1000)

    A Mutator can use a Bender to transform the locations
    for its masters as well as its instances.
    Great care has to be taken not to mix up transformed / untransformed.
    So the changes in Mutator are small.

    
"""
class Bender(object):
    # object with a dictionary of warpmaps
    # call instance with a location to bend it
    def __init__(self, warpDict):
        self.warps = {}
        self.maps = {}    # not needed?
        for axisName, obj in warpDict.items():
            if type(obj)==list:
                self._makeWarpFromList(axisName, obj)
            elif hasattr(obj, '__call__'):
                # self.warps[axisName] = WarpFunctionWrapper(obj)
                self.warps[axisName] = obj
    
    def getMap(self, axisName):
        return self.maps.get(axisName, [])
            
    def _makeWarpFromList(self, axisName, warpMap):
        if not warpMap:
            warpMap = [(0,0), (1000,1000)]
        self.maps[axisName] = warpMap
        items = []
        for x, y in warpMap:
            items.append((Location(w=x), y))
        m = WarpMutator()
        items.sort()
        bias = biasFromLocations([loc for loc, obj in items], True)
        m.setBias(bias)
        n = None
        ofx = []
        onx = []
        for loc, obj in items:
            if (loc-bias).isOrigin():
                m.setNeutral(obj)
                break
        if m.getNeutral() is None:
            raise MutatorError("Did not find a neutral for this system", m)
        for loc, obj in items:
            lb = loc-bias
            if lb.isOrigin(): continue
            if lb.isOnAxis():
                onx.append((lb, obj-m.getNeutral()))
            else:
                ofx.append((lb, obj-m.getNeutral()))
        for loc, obj in onx:
            m.addDelta(loc, obj, punch=False,  axisOnly=True)
        for loc, obj in ofx:
            m.addDelta(loc, obj, punch=True,  axisOnly=True)
        self.warps[axisName] = m

    def __call__(self, loc):
        # bend a location according to the defined warps
        new = loc.copy()
        for dim, warp in self.warps.items():
            if not dim in loc: continue
            try:
                new[dim] = warp(loc.get(dim))
            except:
                ex_type, ex, tb = sys.exc_info()
                raise MutatorError("A warpfunction \"%s\" (for axis \"%s\") raised \"%s\" at location %s"%(warp.__name__, dim, ex, loc.asString()), loc)
        return new

if __name__ == "__main__":

    # no bender
    assert noBend(Location(a=1234)) == Location(a=1234)

    # linear map, single axis
    w = {'a': [(0, 0), (1000, 1000)]}
    b = Bender(w)
    assert b(Location(a=0)) == Location(a=0)
    assert b(Location(a=500)) == Location(a=500)
    assert b(Location(a=1000)) == Location(a=1000)

    # linear map, single axis
    w = {'a': [(0, 100), (1000, 900)]}
    b = Bender(w)
    assert b(Location(a=0)) == Location(a=100)
    assert b(Location(a=500)) == Location(a=500)
    assert b(Location(a=1000)) == Location(a=900)

    # one split map, single axis
    w = {'a': [(0, 0), (500, 200), (1000, 1000)]}
    b = Bender(w)
    assert b(Location(a=0)) == Location(a=0)
    assert b(Location(a=250)) == Location(a=100)
    assert b(Location(a=500)) == Location(a=200)
    assert b(Location(a=750)) == Location(a=600)
    assert b(Location(a=1000)) == Location(a=1000)

    # now with warp functions
    def warpFunc_1(value):
        return value * 2
    def warpFunc_2(value):
        return value ** 2
    def warpFunc_Error(value):
        return 1/0

    w = {'a': warpFunc_1, 'b': warpFunc_2, 'c': warpFunc_Error}
    b = Bender(w)
    assert b(Location(a=100)) == Location(a=200)
    assert b(Location(b=100)) == Location(b=10000)

    # see if the errors are caught and reported:
    try:
        b(Location(c=-1))
    except:
        ex_type, ex, tb = sys.exc_info()
        err = 'A warpfunction "warpFunc_Error" (for axis "c") raised "integer division or modulo by zero" at location c:-1'
        assert ex.msg == err


