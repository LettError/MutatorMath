# -*- coding: utf-8 -*-
from __future__ import print_function, division
import math, sys
import itertools, operator

from mutatorMath import __version__


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

    def __lt__(self, other):
        if len(self) < len(other):
            return True
        elif len(self) > len(other):
            return False
        self_keys = sorted(self.keys())
        other_keys = sorted(other.keys())
        for i, key in enumerate(self_keys):
            if key < other_keys[i]:
                return True
            elif key > other_keys[i]:
                return False
            if self[key] < other[key]:
                return True
        return False
    
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
            if k not in self:
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
        k = sorted(self.keys())
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
        names = sorted(k for k in self.keys() if self[k]!=0)
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
            >>> l.asDict()['snap']
            -100
            >>> l.asDict()['pop']
            1
        """
        new = {}
        new.update(self)
        return new
    
    def asSortedStringDict(self, roundValue=False):
        """ Return the data in a dict with sorted names and column titles.
        ::

            >>> l = Location(pop=1, snap=(1,10))
            >>> l.asSortedStringDict()[0]['value']
            '1'
            >>> l.asSortedStringDict()[0]['axis']
            'pop'
            >>> l.asSortedStringDict()[1]['axis']
            'snap'
            >>> l.asSortedStringDict()[1]['value']
            '(1,10)'
            
        """
        data = []
        names = sorted(self.keys())
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
        result = []
        for k, v in self.items():
            if isinstance(v, tuple):
                if v > (_EPSILON, ) * len(v) or v < (-_EPSILON, ) * len(v):
                    result.append((k, v))
            elif v > _EPSILON or v < -_EPSILON:
                result.append((k, v))
        return self.__class__(result)
    
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
            if isinstance(value, tuple):
                if (value < (-_EPSILON,) * len(value)
                        or value > (_EPSILON,) * len(value)):
                    return False
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
        dims = list(s.keys())
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
                return isinstance(self[dim], tuple)
            except KeyError:
                # dimension is not present, it should be 0, so not ambivalent
                return False
        for dim, val in self.items():
            if isinstance(val, tuple):
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
            if isinstance(val, tuple):
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
            if isinstance(val, tuple):
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
            if isinstance(val, tuple):
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
    
    def __truediv__(self, factor):
        if factor == 0:
            raise ZeroDivisionError
        if isinstance(factor, tuple):
            if factor[0] == 0 or factor[1] == 0:
                raise ZeroDivisionError
            return self * (1.0/factor[0]) + self * (1.0/factor[1])
        return self * (1.0/factor)
    
    __div__ = __truediv__

    
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
                if axis not in onAxisValues:
                    onAxisValues[axis] = []
                onAxisValues[axis].append(l[axis])
        else:
            offAxis.append(l)
    for l in offAxis:
        ok = False
        for axis in l.keys():
            if axis not in onAxisValues:
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
    sys.exit(doctest.testmod().failed)
