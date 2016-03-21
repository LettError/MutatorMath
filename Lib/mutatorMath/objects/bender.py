import math
from mutatorMath.objects.error import MutatorError
from mutatorMath.objects.location import Location, sortLocations, biasFromLocations
import mutatorMath.objects.mutator

def noBend(loc): return loc

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
        for axisName, d in warpDict.items():
            self._makeWarp(axisName, d)
    
    def getMap(self, axisName):
        return self.maps.get(axisName, [])
            
    def _makeWarp(self, axisName, warpMap):
        if not warpMap:
            warpMap = [(0,0), (1000,1000)]
        self.maps[axisName] = warpMap
        items = []
        for x, y in warpMap:
            items.append((Location(w=x), y))
        m = mutatorMath.objects.mutator.Mutator()
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
            new[dim] = warp.makeInstance(Location(w=loc.get(dim)))
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
