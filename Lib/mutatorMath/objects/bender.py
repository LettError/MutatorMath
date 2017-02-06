
import sys
from mutatorMath.objects.error import MutatorError
from mutatorMath.objects.location import Location, biasFromLocations
import mutatorMath.objects.mutator

def noBend(loc): return loc

class WarpMutator(mutatorMath.objects.mutator.Mutator):
    def __call__(self, value):
        if isinstance(value, tuple):
            # handle split location
            return self.makeInstance(Location(w=value[0])), self.makeInstance(Location(w=value[1]))
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
    def __init__(self, axes):
        # axes dict:
        #   { <axisname>: {'map':[], 'minimum':0, 'maximum':1000, 'default':0, 'tag':'aaaa', 'name':"longname"}}
        warpDict = {}
        self.maps = {}    # not needed?
        self.warps = {}
        for axisName, axisAttributes in axes.items():
            mapData = axisAttributes.get('map', [])
            if type(mapData)==list:
                if mapData==0:
                    # this axis has no bender
                    self.warps[axisName] = None
                else:
                    self._makeWarpFromList(axisName, mapData, axisAttributes['minimum'], axisAttributes['maximum'])
            elif hasattr(mapData, '__call__'):
                self.warps[axisName] = mapData
    
    def __repr__(self):
        return "<Bender %s>"%(str(self.warps.items()))

    def getMap(self, axisName):
        return self.maps.get(axisName, [])
            
    def _makeWarpFromList(self, axisName, warpMap, minimum, maximum):
        if not warpMap:
            warpMap = [(minimum,minimum), (maximum,maximum)]
        self.warps[axisName] = warpMap
        # check for the extremes, add if necessary
        if not sum([a==minimum for a, b in warpMap]):
            warpMap = [(minimum,minimum)] + warpMap
        if not sum([a==maximum for a, b in warpMap]):
            warpMap.append((maximum,maximum))
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
            if warp is None:
                new[dim] = loc[dim]
                continue
            if not dim in loc: continue
            try:
                new[dim] = warp(loc.get(dim))
            except:
                ex_type, ex, tb = sys.exc_info()
                raise MutatorError("A warpfunction \"%s\" (for axis \"%s\") raised \"%s\" at location %s"%(str(warp), dim, ex, loc.asString()), loc)
        return new

if __name__ == "__main__":
    # no bender
    assert noBend(Location(a=1234)) == Location(a=1234)
    assert noBend(Location(a=(12,34))) == Location(a=(12,34))

    # linear map, single axis
    w = {'aaaa':{'map': [(0, 0), (1000, 1000)], 'name':'aaaaAxis', 'tag':'aaaa', 'minimum':0, 'maximum':1000, 'default':0}}
    b = Bender(w)
    assert b(Location(aaaa=0)) == Location(aaaa=0)
    assert b(Location(aaaa=500)) == Location(aaaa=500)
    assert b(Location(aaaa=1000)) == Location(aaaa=1000)

    # linear map, single axis
    #w = {'a': [(0, 100), (1000, 900)]}
    w = {'aaaa':{'map': [(0, 100), (1000, 900)], 'name':'aaaaAxis', 'tag':'aaaa', 'minimum':0, 'maximum':1000, 'default':0}}
    b = Bender(w)
    assert b(Location(aaaa=0)) == Location(aaaa=100)
    assert b(Location(aaaa=500)) == Location(aaaa=500)
    assert b(Location(aaaa=1000)) == Location(aaaa=900)

    # linear map, single axis, not mapped to 1000
    #w = {'a': [(0, 100), (1000, 900)]}
    w = {'aaaa':{'map': [(-1, 2), (0,0), (1, 2)], 'name':'aaaaAxis', 'tag':'aaaa', 'minimum':-1, 'maximum':1, 'default':0}}
    b = Bender(w)
    assert b(Location(aaaa=(-1, 1))) == Location(aaaa=(2,2))
    assert b(Location(aaaa=-1)) == Location(aaaa=2)
    assert b(Location(aaaa=-0.5)) == Location(aaaa=1)
    assert b(Location(aaaa=0)) == Location(aaaa=0)
    assert b(Location(aaaa=0.5)) == Location(aaaa=1)
    assert b(Location(aaaa=1)) == Location(aaaa=2)

    # one split map, single axis
    #w = {'a': [(0, 0), (500, 200), (600, 600)]}
    w = {'aaaa':{'map': [(0, 100), (500, 200), (600, 600)], 'name':'aaaaAxis', 'tag':'aaaa', 'minimum':0, 'maximum':600, 'default':0}}
    b = Bender(w)
    assert b(Location(aaaa=(100, 200))) == Location(aaaa=(120,140))
    assert b(Location(aaaa=0)) == Location(aaaa=100)
    assert b(Location(aaaa=250)) == Location(aaaa=150)
    assert b(Location(aaaa=500)) == Location(aaaa=200)
    assert b(Location(aaaa=600)) == Location(aaaa=600)
    assert b(Location(aaaa=750)) == Location(aaaa=1200)
    assert b(Location(aaaa=1000)) == Location(aaaa=2200)

    # implicit extremes
    w = {'aaaa':{'map': [(500, 200)], 'name':'aaaaAxis', 'tag':'aaaa', 'minimum':0, 'maximum':600, 'default':0}}
    b = Bender(w)
    assert b(Location(aaaa=(250, 100))) == Location(aaaa=(100, 40))
    assert b(Location(aaaa=0)) == Location(aaaa=0)
    assert b(Location(aaaa=250)) == Location(aaaa=100)
    assert b(Location(aaaa=500)) == Location(aaaa=200)
    assert b(Location(aaaa=600)) == Location(aaaa=600)
    assert b(Location(aaaa=750)) == Location(aaaa=1200)
    assert b(Location(aaaa=1000)) == Location(aaaa=2200)

    # now with warp functions
    # warp functions must be able to handle split tuples
    def warpFunc_1(value):
        if isinstance(value, tuple):
            return value[0]*2, value[1]*2
        return value * 2
    def warpFunc_2(value):
        if isinstance(value, tuple):
            return value[0] ** 2, value[1] ** 2
        return value ** 2
    def warpFunc_Error(value):
        return 1/0

    w = {   'aaaa':{'map': warpFunc_1, 'name':'aaaaAxis', 'tag':'aaaa', 'minimum':0, 'maximum':1000, 'default':0},
            'bbbb':{'map': warpFunc_2, 'name':'bbbbAxis', 'tag':'bbbb', 'minimum':0, 'maximum':1000, 'default':0},
        }
    # w = {'a': warpFunc_1, 'b': warpFunc_2, 'c': warpFunc_Error}
    b = Bender(w)
    assert b(Location(aaaa=(100, -100))) == Location(aaaa=(200.000,-200.000))
    assert b(Location(aaaa=100)) == Location(aaaa=200)
    assert b(Location(bbbb=100)) == Location(bbbb=10000)

    # # see if the errors are caught and reported:
    try:
        b(Location(c=-1))
    except:
        ex_type, ex, tb = sys.exc_info()
        err = 'A warpfunction "warpFunc_Error" (for axis "c") raised "integer division or modulo by zero" at location c:-1'
        assert ex.msg == err


