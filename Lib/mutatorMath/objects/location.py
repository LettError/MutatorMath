# -*- coding: utf-8 -*-

from types import TupleType
import math, sys
import itertools, operator

__version__ = "1.6"

_EPSILON = sys.float_info.epsilon

__all__ =  ["Location", "sortLocations"]

def numberToString(value):
    # return a nicely formatted string of this value
    # return tuples as a tuple-looking string with formatted numbers
    # return ints as ints, no commas
    # return floats as compact rounded value
    if value is None:
        return "None"
    if type(value)==tuple:
        t = []
        for v in value:
            t.append(numberToString(v))
        return "(%s)"%(",".join(t))
    if int(value) == value:
        # it is an int
        return "%d"%(value)
    return "%3.3f"%value
    

class Location(dict):
    """
    A object subclassed from dict to store n-dimensional locations.
    
    - key is dimension or axis name
    - value is the coordinate.

    - Location objects behave like numbers.
    - If a specific dimension is missing, assume it is zero.
    - Convert to and from dict, tuple.
    
    ::
    
        >>> l = Location(pop=1, snap=-100)
        >>> print(l)
        <Location pop:1, snap:-100 >
        

    Location objects can be used as math objects:

    ::

        >>> l = Location(pop=1)
        >>> l * 2
        <Location pop:2 >
        >>> 2 * l
        <Location pop:2 >
        >>> l / 2
        <Location pop:0.500 >
        
        >>> l = Location(pop=1)
        >>> m = Location(pop=10)
        >>> l + m
        <Location pop:11 >

        >>> l = Location(pop=1)
        >>> m = Location(pop=10)
        >>> l - m
        <Location pop:-9 >
    """
    
    def __repr__(self):
        t = ["<%s"%self.__class__.__name__]
        t.append(self.asString())
        t.append(">")
        return " ".join(t)
    
    def expand(self, axisNames):
        """
        Expand the location with zero values for all axes in axisNames that aren't filled in the current location.
        ::

            >>> l = Location(pop=1)
            >>> l.expand(['snap', 'crackle'])
            >>> print(l)
            <Location crackle:0, pop:1, snap:0 >
        """
        for k in axisNames:
            if not self.has_key(k):
                self[k] = 0
    
    def copy(self):
        """
        Return a copy of this location.
        ::
            
            >>> l = Location(pop=1, snap=0)
            >>> l.copy()
            <Location pop:1, snap:0 >

        """
        new = self.__class__()
        new.update(self)
        return new
        
    def fromTuple(self, locationTuple):
        """
        Read the coordinates from a tuple.
        ::
            
            >>> t = (('pop', 1), ('snap', -100))
            >>> l = Location()
            >>> l.fromTuple(t)
            >>> print(l)
            <Location pop:1, snap:-100 >

        """
        for key, value in locationTuple:
            try:
                self[key] = float(value)
            except TypeError:
                self[key] = tuple([float(v) for v in value])
        
    def asTuple(self):
        """Return the location as a tuple.
        Sort the dimension names alphabetically.
        ::
        
            >>> l = Location(pop=1, snap=-100)
            >>> l.asTuple()
            (('pop', 1), ('snap', -100))
        """
        t = []
        k = self.keys()
        k.sort()
        for key in k:
            t.append((key, self[key]))
        return tuple(t)
    
    def getType(self, short=False):
        """Return a string describing the type of the location, i.e. origin, on axis, off axis etc.

        ::
            
            >>> l = Location()
            >>> l.getType()
            'origin'
            >>> l = Location(pop=1)
            >>> l.getType()
            'on-axis, pop'
            >>> l = Location(pop=1, snap=1)
            >>> l.getType()
            'off-axis, pop snap'
            >>> l = Location(pop=(1,2))
            >>> l.getType()
            'on-axis, pop, split'
        """
        if self.isOrigin():
            return "origin"
        t = []
        onAxis = self.isOnAxis()
        if onAxis is False:
            if short:
                t.append("off-axis")
            else:
                t.append("off-axis, "+ " ".join(self.getActiveAxes()))
        else:
            if short:
                t.append("on-axis")
            else:
                t.append("on-axis, %s"%onAxis)
        if self.isAmbivalent():
            t.append("split")
        return ', '.join(t)
    
    def getActiveAxes(self):
        """
        Return a list of names of axes which are not zero
        ::
        
            >>> l = Location(pop=1, snap=0, crackle=1)
            >>> l.getActiveAxes()
            ['crackle', 'pop']
        """
        names = [k for k in self.keys() if self[k]!=0]
        names.sort()
        return names
        
    def asString(self, strict=False):
        """
        Return the location as a string.
        ::
        
            >>> l = Location(pop=1, snap=(-100.0, -200))
            >>> l.asString()
            'pop:1, snap:(-100.000,-200.000)'
        """
        if len(self.keys())==0:
            return "origin"
        v = []
        n = []
        try:
            for name, value in self.asTuple():
                s = ''
                if value is None:
                    s = "None"
                elif type(value) == tuple or type(value) == list:
                    s = "(%.3f,%.3f)"%(value[0], value[1])
                elif int(value) == value:
                    s = "%d"%(int(value))
                else:
                    s = "%.3f"%(value)
                if s != '':
                    n.append("%s:%s"%(name, s))
            return ", ".join(n)
        except TypeError:
            import traceback
            print("Location value error:", name, value)
            for key, value in self.items():
                print("\t\tkey:", key)
                print("\t\tvalue:", value)
            traceback.print_exc()
            return "error"

    def asDict(self):
        """
        Return the location as a plain python dict.
        ::
        
            >>> l = Location(pop=1, snap=-100)
            >>> l.asDict()
            {'snap': -100, 'pop': 1}
        """
        new = {}
        new.update(self)
        return new
    
    def asSortedStringDict(self, roundValue=False):
        """ Return the data in a dict with sorted names and column titles.
        ::

            >>> l = Location(pop=1, snap=(1,10))
            >>> l.asSortedStringDict()
            [{'value': '1', 'axis': 'pop'}, {'value': '(1,10)', 'axis': 'snap'}]
            
        """
        data = []
        names = self.keys()
        names.sort()
        for n in names:
            data.append({'axis':n, 'value':numberToString(self[n])})
        return data
        
    def strip(self):
        """ Remove coordinates that are zero, the opposite of expand().

        ::

            >>> l = Location(pop=1, snap=0)
            >>> l.strip()
            <Location pop:1 >
            
        """
        return self.__class__([(k, v) for k, v in self.items() if v > _EPSILON or v < -_EPSILON])
    
    def common(self, other):
        """
        Return two objects with the same dimensions if they lie in the same orthogonal plane.
        ::

            >>> l = Location(pop=1, snap=2)
            >>> m = Location(crackle=1, snap=3)
            >>> l.common(m)
            (<Location snap:2 >, <Location snap:3 >)
        """
        selfDim = set(self.keys())
        otherDim = set(other.keys())
        dims = selfDim | otherDim
        newSelf = None
        newOther = None
        for dim in dims:
            sd = self.get(dim, None)
            od = other.get(dim, None)
            if sd is None or od is None:
                # axis is missing in one or the other
                continue
            if -_EPSILON < sd < _EPSILON and -_EPSILON < od < _EPSILON:
                # values are both zero
                continue
            if newSelf is None:
                newSelf = self.__class__()
            if newOther is None:
                newOther = self.__class__()
            newSelf[dim] = self[dim]
            newOther[dim] = other[dim]
        return newSelf, newOther
    
    #
    #
    #   tests
    #
    #
    
    def isOrigin(self):
        """
        Return True if the location is at the origin.
        ::
            >>> l = Location(pop=1)
            >>> l.isOrigin()
            False
            >>> l = Location()
            >>> l.isOrigin()
            True
        """
        for name, value in self.items():
            if value < -_EPSILON or value > _EPSILON:
                return False
        return True
        
    def isOnAxis(self):
        """
        Returns statements about this location:
        
            *   False if the location is not on-axis
            *   The name of the axis if it is on-axis
            *   None if the Location is at the origin

        Note: this is only valid for an unbiased location.
        ::

            >>> l = Location(pop=1)
            >>> l.isOnAxis()
            'pop'
            >>> l = Location(pop=1, snap=1)
            >>> l.isOnAxis()
            False
            >>> l = Location()
            >>> l.isOnAxis() is None
            True
        """     
        new = self.__class__()
        new.update(self)
        s = new.strip()
        dims = s.keys()
        if len(dims)> 1:
            return False
        elif len(dims)==1:
            return dims[0]
        return None
        
    def isAmbivalent(self, dim=None):
        """
        Return True if any of the factors are in fact tuples.
        If a dimension name is given only that dimension is tested.
        ::
            >>> l = Location(pop=1)
            >>> l.isAmbivalent()
            False
            >>> l = Location(pop=1, snap=(100, -100))
            >>> l.isAmbivalent()
            True
        """
        if dim is not None:
            try:
                return type(self[dim]) == TupleType
            except KeyError:
                # dimension is not present, it should be 0, so not ambivalent
                return False
        for dim, val in self.items():
            if type(val) == TupleType:
                return True
        return False
    
    def split(self):
        """
        Split an ambivalent location into 2. One for the x, the other for the y.
        ::

            >>> l = Location(pop=(-5,5))
            >>> l.split()
            (<Location pop:-5 >, <Location pop:5 >)
        """
        x = self.__class__()
        y = self.__class__()
        for dim, val in self.items():
            if type(val) == TupleType:
                x[dim] = val[0]
                y[dim] = val[1]
            else:
                x[dim] = val
                y[dim] = val
        return x, y

    def spliceX(self):
        """
        Return a copy with the x values preferred for ambivalent locations.
        ::

            >>> l = Location(pop=(-5,5))
            >>> l.spliceX()
            <Location pop:-5 >
        """
        new = self.__class__()
        for dim, val in self.items():
            if type(val) == TupleType:
                new[dim] = val[0]
            else:
                new[dim] = val
        return new
        
    def spliceY(self):
        """
        Return a copy with the y values preferred for ambivalent locations.
        ::

            >>> l = Location(pop=(-5,5))
            >>> l.spliceY()
            <Location pop:5 >
        """
        new = self.__class__()
        for dim, val in self.items():
            if type(val) == TupleType:
                new[dim] = val[1]
            else:
                new[dim] = val
        return new
        
    def distance(self, other=None):
        """Return the geometric distance to the other location.
        If no object is provided, this will calculate the distance to the origin.

        ::

            >>> l = Location(pop=100)
            >>> m = Location(pop=200)
            >>> l.distance(m)
            100.0
            >>> l = Location()
            >>> m = Location(pop=200)
            >>> l.distance(m)
            200.0
            >>> l = Location(pop=3, snap=5)
            >>> m = Location(pop=7, snap=8)
            >>> l.distance(m)
            5.0
        """
        t = 0
        if other is None:
            other = self.__class__()
        for axisName in set(self.keys()) | set(other.keys()):
            t += (other.get(axisName,0)-self.get(axisName,0))**2
        return math.sqrt(t)
    
    def sameAs(self, other):
        """
        Check if this is the same location.
        ::
        
            >>> l = Location(pop=5, snap=100)
            >>> m = Location(pop=5.0, snap=100.0)
            >>> l.sameAs(m)
            0
            >>> l = Location(pop=5, snap=100)
            >>> m = Location(pop=5.0, snap=100.0001)
            >>> l.sameAs(m)
            -1
        """
        if not hasattr(other, "get"):
            return -1
        d = self.distance(other)
        if d < _EPSILON:
            return 0
        return -1
    
    # math operators
    def __add__(self, other):
        new = self.__class__()
        new.update(self)
        new.update(other)
        selfDim = set(self.keys())
        otherDim = set(other.keys())
        for key in selfDim & otherDim:
            ts = type(self[key])!=tuple
            to = type(other[key])!=tuple
            if ts:
                sx = sy = self[key]
            else:
                sx = self[key][0]
                sy = self[key][1]
            if to:
                ox = oy = other[key]
            else:
                ox = other[key][0]
                oy = other[key][1]
            x = sx+ox
            y = sy+oy
            if x==y:
                new[key] = x
            else:
                new[key] = x,y
        return new

    def __sub__(self, other):
        new = self.__class__()
        new.update(self)
        for key, value in other.items():
            try:
                new[key] = -value
            except TypeError:
                new[key] = (-value[0], -value[1])
        selfDim = set(self.keys())
        otherDim = set(other.keys())
        for key in selfDim & otherDim:
            ts = type(self[key])!=tuple
            to = type(other[key])!=tuple
            if ts:
                sx = sy = self[key]
            else:
                sx = self[key][0]
                sy = self[key][1]
            if to:
                ox = oy = other[key]
            else:
                ox = other[key][0]
                oy = other[key][1]
            x = sx-ox
            y = sy-oy
            if x==y:
                new[key] = x
            else:
                new[key] = x,y
        return new
    
    def __mul__(self, factor):
        new = self.__class__()
        if isinstance(factor, tuple):
            for key, value in self.items():
                if type(value) == tuple:
                    new[key] = factor[0] * value[0], factor[1] * value[1]
                else:
                    new[key] = factor[0] * value, factor[1] * value
        else:
            for key, value in self.items():
                if type(value) == tuple:
                    new[key] = factor * value[0], factor * value[1]
                else:
                    new[key] = factor * value
        return new
    
    __rmul__ = __mul__
    
    def __div__(self, factor):
        if factor == 0:
            raise ZeroDivisionError
        if isinstance(factor, tuple):
            if factor[0] == 0 or factor[1] == 0:
                raise ZeroDivisionError
            return self * (1.0/factor[0]) + self * (1.0/factor[1])
        return self * (1.0/factor)
    
    def transform(self, transformDict):
        if transformDict is None:
            return self
        new = self.__class__()
        for dim, (offset, scale) in transformDict.items():
            new[dim] = (self.get(dim,0)+offset)*scale
        return new

def sortLocations(locations):
    """ Sort the locations by ranking:
            1.  all on-axis points
            2.  all off-axis points which project onto on-axis points
                these would be involved in master to master interpolations
                necessary for patching. Projecting off-axis masters have
                at least one coordinate in common with an on-axis master.
            3.  non-projecting off-axis points, 'wild' off axis points
                These would be involved in projecting limits and need to be patched.
    """
    onAxis = []
    onAxisValues = {}
    offAxis = []
    offAxis_projecting = []
    offAxis_wild = []
    # first get the on-axis points
    for l in locations:
        if l.isOrigin():
            continue
        if l.isOnAxis():
            onAxis.append(l)
            for axis in l.keys():
                if not onAxisValues.has_key(axis):
                    onAxisValues[axis] = []
                onAxisValues[axis].append(l[axis])
        else:
            offAxis.append(l)
    for l in offAxis:
        ok = False
        for axis in l.keys():
            if not onAxisValues.has_key(axis):
                continue
            if l[axis] in onAxisValues[axis]:
                ok = True
        if ok:
            offAxis_projecting.append(l)
        else:
            offAxis_wild.append(l)
    return onAxis, offAxis_projecting, offAxis_wild

def biasFromLocations(locs, preferOrigin=True):
    """
        Find the vector that translates the whole system to the origin. 
    """
    dims = {}
    locs.sort()
    for l in locs:
        for d in l.keys():
            if not d in dims:
                dims[d] = []
            v = l[d]
            if type(v)==tuple:
                dims[d].append(v[0])
                dims[d].append(v[1])
            else:
                dims[d].append(v)
    candidate = Location()
    for k in dims.keys():
        dims[k].sort()
        v = mostCommon(dims[k])
        if dims[k].count(v) > 1:
            # add the dimension with two or more hits
            candidate[k] = mostCommon(dims[k])
    matches = []
    # 1. do we have an exact match?
    for l in locs:
        if candidate == l:
            return l
    # 2. find a location that matches candidate (but has more dimensions)
    for l in locs:
        ok = True
        for k, v in candidate.items():
            if l.get(k)!=v:
                ok = False
                break
        if ok:
            if not l in matches:
                matches.append(l)
    matches.sort()
    if len(matches)>0:
        if preferOrigin:
            for c in matches:
                if c.isOrigin():
                    return c
        return matches[0]
    # 3. no matches. Find the best from the available locations
    results = {}
    for bias in locs:
        rel = []
        for l in locs:
            rel.append((l - bias).isOnAxis())
        c = rel.count(False)
        if not c in results:
            results[c] = []
        results[c].append(bias)
    if results:
        candidates = results[min(results.keys())]
        if preferOrigin:
            for c in candidates:
                if c.isOrigin():
                    return c
        candidates.sort()
        return candidates[0]
    return Location()
                    
def mostCommon(L):
    """
        #   http://stackoverflow.com/questions/1518522/python-most-common-element-in-a-list
        
        >>> mostCommon([1, 2, 2, 3])
        2
        >>> mostCommon([1, 2, 3])
        1
        >>> mostCommon([-1, 2, 3])
        -1
        >>> mostCommon([-1, -2, -3])
        -1
        >>> mostCommon([-1, -2, -3, -1])
        -1
        >>> mostCommon([-1, -1, -2, -2])
        -1
        >>> mostCommon([0, 0.125, 0.275, 1])
        0
        >>> mostCommon([0, 0.1, 0.4, 0.4])
        0.4
    """
    # get an iterable of (item, iterable) pairs
    SL = sorted((x, i) for i, x in enumerate(L))
    # print 'SL:', SL
    groups = itertools.groupby(SL, key=operator.itemgetter(0))
    # auxiliary function to get "quality" for an item
    def _auxfun(g):
        item, iterable = g
        count = 0
        min_index = len(L)
        for _, where in iterable:
            count += 1
            min_index = min(min_index, where)
        # print 'item %r, count %r, minind %r' % (item, count, min_index)
        return count, -min_index
    # pick the highest-count/earliest item
    return max(groups, key=_auxfun)[0]

    
if __name__ == "__main__":

    import doctest

    def _testBiasFromLocations(bias, locs):
        """ 
            # Find the designspace vector for the best bias.
            # Test results: (<number of on-axis locations>, <number of off-axis locations>)

            >>> locs = [Location(a=10), Location(a=10, b=10, c=10), Location(a=10, c=15), Location(a=5, c=15)]
            >>> bias = biasFromLocations(locs)
            >>> bias
            <Location a:10, c:15 >
            >>> _testBiasFromLocations(bias, locs)
            (2, 1)
            
            >>> locs = [Location(a=10, b=0), Location(a=5, b=10), Location(a=20, b=0)]
            >>> bias = biasFromLocations(locs)
            >>> bias
            <Location a:10, b:0 >
            >>> _testBiasFromLocations(bias, locs)
            (1, 1)
            
            >>> locs = [Location(a=10, b=300), Location(a=20, b=300), Location(a=20, b=600), Location(a=30, b=300)]
            >>> bias = biasFromLocations(locs)
            >>> bias
            <Location a:20, b:300 >
            >>> _testBiasFromLocations(bias, locs)
            (3, 0)
            
            >>> locs = [Location(a=-10, b=300), Location(a=0, b=400), Location(a=20, b=300)]
            >>> bias = biasFromLocations(locs)
            >>> bias
            <Location a:-10, b:300 >
            >>> _testBiasFromLocations(bias, locs)
            (1, 1)

            >>> locs = [Location(wt=0, wd=500),
            ...     Location(wt=1000,  wd=900),
            ...     Location(wt=1200,  wd=900),
            ...     Location(wt=-200,  wd=600),
            ...     Location(wt=0,     wd=600),
            ...     Location(wt=1000,  wd=600),
            ...     Location(wt=1200,  wd=600),
            ...     Location(wt=-200,  wd=300),
            ...     Location(wt=0,     wd=300),]
            >>> bias = biasFromLocations(locs)
            >>> bias
            <Location wd:600, wt:0 >
            >>> _testBiasFromLocations(bias, locs)
            (5, 3)

            >>> locs = [
            ...     Location(wt=1,     sz=0),
            ...     Location(wt=0,     sz=0),
            ...     Location(wt=0.275, sz=0),
            ...     Location(wt=0.275, sz=1),
            ...     Location(wt=1,     sz=1),
            ...     Location(wt=0.125, sz=0.4),
            ...     Location(wt=1,     sz=0.4),
            ...     Location(wt=0.6,   sz=0.4),
            ...     Location(wt=0,     sz=0.4),
            ...     Location(wt=0.275, sz=0.4),
            ...     Location(wt=0,     sz=1),
            ...     Location(wt=0.125, sz=1),
            ...     Location(wt=0.6,   sz=0),
            ...     Location(wt=0.125, sz=0),]
            >>> bias = biasFromLocations(locs)
            >>> bias
            <Location sz:0, wt:0 >
            >>> _testBiasFromLocations(bias, locs)
            (6, 7)

            # Nothing lines up
            >>> locs = [
            ...     Location(pop=1),
            ...     Location(snap=1),
            ...     Location(crackle=1)]
            >>> bias = biasFromLocations(locs)
            >>> bias
            <Location crackle:1 >
            >>> _testBiasFromLocations(bias, locs)
            (0, 2)

            # ... why crackle? because it sorts first
            >>> locs.sort()
            >>> locs
            [<Location crackle:1 >, <Location pop:1 >, <Location snap:1 >]

            # Two things line up
            >>> locs = [
            ...     Location(pop=-1),
            ...     Location(pop=1),]
            >>> bias = biasFromLocations(locs)
            >>> bias
            <Location pop:-1 >
            >>> _testBiasFromLocations(bias, locs)
            (1, 0)

            # Two things line up
            >>> locs = [
            ...     Location(pop=-1, snap=-1),
            ...     Location(pop=1, snap=0),
            ...     Location(pop=1, snap=1),
            ...     Location(pop=1, snap=1),
            ...     ]
            >>> bias = biasFromLocations(locs)
            >>> bias
            <Location pop:1, snap:1 >
            >>> _testBiasFromLocations(bias, locs)
            (2, 1)

            # Almost Nothing Lines Up 1
            # An incomplete set of masters can 
            # create a situation in which there is nothing to interpolate.
            # However, we still need to find a bias.
            >>> locs = [
            ...     Location(wt=1,     sz=0.4),
            ...     Location(wt=0.275, sz=0.4),
            ...     Location(wt=0,     sz=1),
            ...     Location(wt=0.125, sz=0),]
            >>> bias = biasFromLocations(locs)
            >>> bias
            <Location sz:0.400, wt:0.275 >
            >>> _testBiasFromLocations(bias, locs)
            (1, 2)

            # Almost Nothing Lines Up 2
            >>> locs = [
            ...     Location(wt=1,     sz=0.4),
            ...     Location(wt=0.275, sz=0.4),
            ...     Location(wt=0,     sz=1),
            ...     Location(wt=0.6,   sz=1),
            ...     Location(wt=0.125, sz=0),]
            >>> bias = biasFromLocations(locs)
            >>> bias
            <Location sz:0.400, wt:0.275 >
            >>> _testBiasFromLocations(bias, locs)
            (1, 3)

            # A square on the origin
            >>> locs = [
            ...     Location(wt=0,     wd=0),
            ...     Location(wt=1,     wd=0),
            ...     Location(wt=0,     wd=1),
            ...     Location(wt=1,     wd=1),]
            >>> bias = biasFromLocations(locs)
            >>> bias
            <Location wd:0, wt:0 >
            >>> _testBiasFromLocations(bias, locs)
            (2, 1)

            # A square, not on the origin
            >>> locs = [
            ...     Location(wt=100,     wd=100),
            ...     Location(wt=200,     wd=100),
            ...     Location(wt=100,     wd=200),
            ...     Location(wt=200,     wd=200),]
            >>> bias = biasFromLocations(locs)
            >>> bias
            <Location wd:100, wt:100 >
            >>> _testBiasFromLocations(bias, locs)
            (2, 1)

            # A square, not on the origin
            >>> locs = [
            ...     Location(wt=200,     wd=100),
            ...     Location(wt=100,     wd=200),
            ...     Location(wt=200,     wd=200),]
            >>> bias = biasFromLocations(locs)
            >>> bias
            <Location wd:200, wt:200 >
            >>> _testBiasFromLocations(bias, locs)
            (2, 0)

            # Two axes, three masters
            >>> locs = [
            ...     Location(ct=0,       wd=0),
            ...     Location(ct=0,       wd=1000),
            ...     Location(ct=100,     wd=1000),]
            >>> bias = biasFromLocations(locs)
            >>> bias
            <Location ct:0, wd:1000 >

            >>> _testBiasFromLocations(bias, locs)
            (2, 0)

            # Complex 4 D space
            >>> locs = [
            ...     Location(A=0,    H=0,    G=1000, W=0),
            ...     Location(A=0,    H=0,    G=1000, W=700),
            ...     Location(A=0,    H=0,    G=1000, W=1000),
            ...     Location(A=0,    H=1000, G=0,    W=200),
            ...     Location(A=0,    H=1000, G=0,    W=300),
            ...     Location(A=0,    H=1000, G=0,    W=700),
            ...     Location(A=0,    H=1000, G=0,    W=1000),
            ...     Location(A=1000, H=0,    G=0,    W=0),]
            >>> bias = biasFromLocations(locs)
            >>> bias
            <Location A:0, G:0, H:1000, W:200 >

            >>> locs = [
            ...     Location(S=0,    U=0,      Wt=54,    Wd=385),
            ...     Location(S=0,    U=268,    Wt=54,    Wd=1000),
            ...     Location(S=8,    U=550,    Wt=851,   Wd=126),
            ...     Location(S=8,    U=868,    Wt=1000,  Wd=1000),]
            >>> bias = biasFromLocations(locs)
            >>> bias
            <Location S:0, U:268, Wd:1000, Wt:54 >


            # empty locs
            >>> locs = []
            >>> bias = biasFromLocations(locs)
            >>> bias
            <Location origin >
        """
        rel = []
        # translate the test locations over the bias
        for l in locs:
            rel.append((l - bias).isOnAxis())
        # MUST have one origin        
        assert None in rel  
        # how many end up off-axis?
        offAxis = rel.count(False)
        # how many end up on-axis?
        onAxis = len(rel)-offAxis-1
        # a good bias has more masters at on-axis locations.
        return onAxis, offAxis

    def test_common():
        """ Make a new location with only the dimensions that the two have in common. 
        
        >>> a = Location(pop=.25, snap=.5, snip=10)
        >>> b = Location(pop=-.35, snap=.6, pip=10)
        >>> [n.asTuple() for n in a.common(b)]
        [(('pop', 0.25), ('snap', 0.5)), (('pop', -0.35), ('snap', 0.6))]
        
        """

    def test_misc():
        """
        >>> l = Location(apop=-1, bpop=10, cpop=-100)
        >>> l.isOnAxis()
        False
        
        # remove empty dimensions
        >>> a = Location(pop=.25, snap=1, plop=0)
        >>> a.strip().asTuple()
        (('pop', 0.25), ('snap', 1))
        
        # add dimensions, set to 0
        >>> a = Location(pop=.25, snap=1)
        >>> a.expand(['plop', 'flop'])
        >>> a.asTuple()
        (('flop', 0), ('plop', 0), ('pop', 0.25), ('snap', 1))
        
        # create a location from a list of name / value tuples.
        >>> a = Location()
        >>> t = [('weight', 1),  ('width', 2), ('zip', 3)]
        >>> a.fromTuple(t)
        >>> a
        <Location weight:1, width:2, zip:3 >
        """
        
    def test_onAxis():
        """
        # origin will return None
        >>> l = Location(pop=0, aap=0, lalala=0, poop=0)
        >>> l.isOnAxis()

        # on axis will return axis name
        >>> l = Location(pop=0, aap=1, lalala=0, poop=0)
        >>> l.isOnAxis()
        'aap'
        
        # off axis will return False
        >>> l = Location(pop=0, aap=1, lalala=1, poop=0)
        >>> l.isOnAxis()
        False
        """
    
    def test_distance():
        """
        # Hypotenuse distance between two locations.
            
        >>> a = Location(pop=0, snap=0)
        >>> b = Location(pop=100, snap=0)
        >>> a.distance(b)
        100.0

        >>> a = Location(pop=0, snap=3)
        >>> b = Location(pop=4, snap=0)
        >>> a.distance(b)
        5.0

        >>> a = Location()
        >>> b = Location(pop=3, snap=4)
        >>> a.distance(b)
        5.0
        """
    
    def test_limits_sorts():
        """ Test some of the functions that handle Locations.
        
        # get the extent of a group of locations.
        >>> a = Location(pop=.25, snap=1, plop=0)
        >>> b = Location(pop=-1, aap=10)
        >>> c = Location(pop=.25, snap=.5)
        >>> d = Location(pop=.35, snap=1)
        >>> e = Location(pop=1)
        >>> f = Location(snap=1)
        >>> l = [a, b, c, d, e, f]
        >>> test = Location(pop=.5, snap=.5)
        >>> from mutatorMath.objects.mutator import getLimits
        >>> getLimits(l, test)
        {'snap': (None, 0.5, None), 'pop': (0.35, None, 1)}

        # sort a group of locations
        >>> sortLocations(l)
        ([<Location pop:1 >, <Location snap:1 >], [<Location plop:0, pop:0.250, snap:1 >, <Location pop:0.350, snap:1 >], [<Location aap:10, pop:-1 >, <Location pop:0.250, snap:0.500 >])

        >>> a1, a2, a3 = sortLocations(l)

        # assert that each location in a1 is on axis, 
        >>> sum([a.isOnAxis() is not None and a.isOnAxis() is not False for a in a1])
        2

        # assert that each location in a1 is off axis, 
        >>> sum([a.isOnAxis() is False for a in a2])
        2

        # how to test for wild locations? Can only see if they're offAxis. Relevant?
        >>> sum([a.isOnAxis() is False for a in a3])
        2
        """
        
    def test_ambivalence():
        """ Test ambivalence qualities of locations.
        
        >>> a = Location(pop=(.25, .33), snap=1, plop=0)
        >>> b = Location(pop=.25, snap=1, plop=0)
        >>> a.isAmbivalent()
        True
        >>> b.isAmbivalent()
        False
        >>> a.spliceX().asTuple() == (('plop', 0), ('pop', 0.25), ('snap', 1))
        True
        >>> a.spliceY().asTuple() == (('plop', 0), ('pop', 0.33), ('snap', 1))
        True
        >>> b.spliceX() == b.spliceY()
        True
        
        >>> a = Location(pop=(.25, .33), snap=1, plop=0)
        >>> a * 2
        <Location plop:0, pop:(0.500,0.660), snap:2 >
        >>> a * (2,0)
        <Location plop:(0.000,0.000), pop:(0.500,0.000), snap:(2.000,0.000) >
        """     

    def test_asString():
        """ Test the conversions to string.
        >>> a = Location(pop=(.25, .33), snap=1.0, plop=0)
        >>> assert a.asString(strict=False) == "plop:0, pop:(0.250,0.330), snap:1"
        >>> assert a.asString(strict=True) == "plop:0, pop:(0.250,0.330), snap:1"

        >>> a = Location(pop=0)
        >>> assert a.asString() == "pop:0"
        >>> assert a.asString(strict=True) == "pop:0"

        >>> a = Location(pop=-1, sip=1)
        >>> assert a.asString() == "pop:-1, sip:1"
        >>> assert a.asString(strict=True) == "pop:-1, sip:1"
        >>> a = Location()
        >>> assert a.asString() == "origin"

        # more string conversions
        >>> a = Location(pop=1)
        >>> assert a.asSortedStringDict() == [{'value': '1', 'axis': 'pop'}]
        >>> a = Location(pop=(0,1))
        >>> assert a.asSortedStringDict() == [{'value': '(0,1)', 'axis': 'pop'}]

        # a description of the type of location
        >>> assert Location(a=1, b=0, c=0).getType() == "on-axis, a"
        >>> assert Location(a=1, b=2).getType() == "off-axis, a b"
        >>> assert Location(a=1).getType() == "on-axis, a"
        >>> assert Location(a=(1,1), b=2).getType() == "off-axis, a b, split"
        >>> assert Location().getType() == "origin"
        """
        

    def test_comparisons():
        """ Test the math comparison qualities.
            The equal operator is useful.
            The < and > operators make assumptions about the geometry that might not be appropriate.

            >>> a = Location()
            >>> a.isOrigin()
            True
            >>> b = Location(pop=2)
            >>> c = Location(pop=2)
            
            >>> b.distance(a)
            2.0
            >>> a.distance(b)
            2.0
                        
            >>> assert (a>b) == False
            >>> assert (c<b) == False
            >>> assert (c==b) == True

        """

    def test_sorting():
        """ Test the sorting qualities.

            >>> a = Location(pop=0)
            >>> b = Location(pop=1)
            >>> c = Location(pop=2)
            >>> d = Location(pop=-1)
            >>> l = [b, d, a, c]
            >>> l.sort()
            >>> l
            [<Location pop:-1 >, <Location pop:0 >, <Location pop:1 >, <Location pop:2 >]
            >>> e = Location(pop=1, snap=1)
            >>> l = [a, e]
            >>> l.sort()
            >>> l
            [<Location pop:0 >, <Location pop:1, snap:1 >]
            >>> f = Location(pop=-1, snap=-1)
            >>> l = [a, e, f]
            >>> l.sort()
            >>> l
            [<Location pop:0 >, <Location pop:-1, snap:-1 >, <Location pop:1, snap:1 >]
            >>> l = [Location(pop=-1), Location(pop=1)]
            >>> l.sort()
            >>> l
            [<Location pop:-1 >, <Location pop:1 >]


        """

    def test_basicMath():
        """ Test the basic mathematical properties of Location.
        
        # addition
        >>> Location(a=1) + Location(a=2) == Location(a=3)
        True

        # addition of ambivalent location
        >>> Location(a=1) + Location(a=(2, 1)) == Location(a=(3,2))
        True

        # subtraction
        >>> Location(a=2) - Location(a=1) == Location(a=1)
        True

        # subtraction of ambivalent location
        >>> Location(a=1) - Location(a=(2, 1)) == Location(a=(-1,0))
        True
        
        >>> Location(a=(1,4)) - Location(a=(2, 1)) == Location(a=(-1,3))
        True
        
        >>> Location(a=(2,1)) - Location(a=(2, 1)) == Location(a=0)
        True

        # multiplication
        >>> Location(a=3) * 3 == Location(a=9)
        True

        # multiplication of ambivalent location
        >>> Location(a=(2, 1)) * 3 == Location(a=(6,3))
        True

        # division
        >>> Location(a=10) / 2 == Location(a=5)
        True
        
        >>> Location(a=10, b=6) / 2 == Location(a=5, b=3)
        True

        # should raise zero division error
        >>> hasRaisedError = False
        >>> try:
        ...     Location(a=5) / 0
        ... except ZeroDivisionError:
        ...     hasRaisedError = True
        >>> assert hasRaisedError

        # interpolation
        >>> a = Location(a=(100, 200))
        >>> b = Location(a=(0, 0))
        >>> f = 0
        >>> a+f*(b-a) == Location(a=(100,200))
        True
        
        >>> f = 0.5
        >>> a+f*(b-a) == Location(a=(50,100))
        True
        
        >>> f = 1
        >>> a+f*(b-a) == Location(a=0)
        True
        
        """
    
    def test17():
        """ See if getLimits can deal with ambiguous locations.
        >>> a = Location(pop=(0.25, 4), snap=1, plop=0)
        >>> print(a.split())
        (<Location plop:0, pop:0.250, snap:1 >, <Location plop:0, pop:4, snap:1 >)
        """

    def regressionTests():
        """ Test all the basic math operations
        
        >>> assert Location(a=1) + Location(a=2) == Location(a=3)           # addition
        >>> assert Location(a=1.0) - Location(a=2.0) == Location(a=-1.0)    # subtraction
        >>> assert Location(a=1.0) * 2 == Location(a=2.0)                   # multiplication
        >>> assert Location(a=1.0) * 0 == Location(a=0.0)                   # multiplication
        >>> assert Location(a=2.0) / 2 == Location(a=1.0)                   # division
    
        >>> assert Location(a=(1,2)) * 2 == Location(a=(2,4))               # multiplication with ambivalence
        >>> assert Location(a=(2,4)) / 2 == Location(a=(1,2))               # division with ambivalence
    
        >>> assert Location(a=(2,4)) - Location(a=1) == Location(a=(1,3)) 
        
         """
    
    doctest.testmod()
