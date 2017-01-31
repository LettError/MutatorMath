from mutatorMath.objects.location import Location, biasFromLocations, sortLocations


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
    >>> limits = getLimits(l, test)
    >>> 'snap' in limits and 'pop' in limits
    True
    >>> limits['snap']
    (None, 0.5, None)
    >>> limits['pop']
    (0.35, None, 1)

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


if __name__ == '__main__':
    import sys
    import doctest
    sys.exit(doctest.testmod().failed)
