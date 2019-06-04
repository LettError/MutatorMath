from mutatorMath.objects.error import MutatorError
from mutatorMath.objects.location import Location, sortLocations, biasFromLocations
from mutatorMath.objects.mutator import Mutator, buildMutator, getLimits


def test_singleAxis(n):
    """
    Tests for a single axis.
    A mutator is created with a single value, 100, on a single axis.

    values we enter should be reproduced
    >>> test_singleAxis(1)
    100.0
    >>> test_singleAxis(0)
    0

    a value in the middle should be in the middle
    >>> test_singleAxis(.5)
    50.0
    >>> test_singleAxis(.99)
    99.0

    extrapolation over zero
    >>> test_singleAxis(-1)
    -100.0
    >>> test_singleAxis(-2)
    -200.0
    >>> test_singleAxis(-1.5)
    -150.0

    extrapolation over value
    >>> test_singleAxis(2)
    200.0

    """
    m = Mutator()
    neutral = 0
    value = 100.0
    m.setNeutral(neutral-neutral)
    m.addDelta(Location(pop=1), value-neutral, deltaName="test")
    return m.getInstance(Location(pop=n)) + neutral


def test_twoAxes(l, n):
    """Test for a system with two axes, 2 values both on-axis.

    >>> test_twoAxes(1, 1)
    0.0
    >>> test_twoAxes(1, 0)
    100.0
    >>> test_twoAxes(0, 1)
    -100.0
    >>> test_twoAxes(2, 0)
    200.0
    >>> test_twoAxes(0, 2)
    -200.0

    a value in the middle should be in the middle
    """
    m = Mutator()
    neutral = 0
    value = 100.0
    m.setNeutral(neutral-neutral)
    m.addDelta(Location(pop=1), value-neutral, deltaName="test1")
    m.addDelta(Location(snap=1), -1*value-neutral, deltaName="test2")
    return m.getInstance(Location(pop=l, snap=n)) + neutral


def test_twoAxesOffAxis(l, n):
    """Test for a system with two axes. Three values, two on-axis, one off-axis.

    >>> test_twoAxesOffAxis(0, 0)
    0
    >>> test_twoAxesOffAxis(1, 1)
    50.0
    >>> test_twoAxesOffAxis(2, 2)
    200.0
    >>> test_twoAxesOffAxis(1, 0)
    100.0
    >>> test_twoAxesOffAxis(0, 1)
    -100.0
    >>> test_twoAxesOffAxis(2, 0)
    200.0
    >>> test_twoAxesOffAxis(0, 2)
    -200.0

    a value in the middle should be in the middle
    """
    m = Mutator()
    neutral = 0
    value = 100.0
    m.setNeutral(neutral-neutral)
    m.addDelta(Location(pop=1), value-neutral, deltaName="test1")
    m.addDelta(Location(snap=1), -1*value-neutral, deltaName="test2")
    m.addDelta(Location(pop=1, snap=1), 50, punch=True, deltaName="test2")
    return m.getInstance(Location(pop=l, snap=n)) + neutral


def test_twoAxesOffAxisSmall(l, n):
    """Test for a system with two axes. Three values, two on-axis, one off-axis.
    >>> test_twoAxesOffAxisSmall(0, 0)
    0
    >>> test_twoAxesOffAxisSmall(1, 1)
    5e-16
    >>> test_twoAxesOffAxisSmall(2, 2)
    2e-15
    >>> test_twoAxesOffAxisSmall(1, 0)
    1e-15
    >>> test_twoAxesOffAxisSmall(0, 1)
    -1e-15
    >>> test_twoAxesOffAxisSmall(2, 0)
    2e-15
    >>> test_twoAxesOffAxisSmall(0, 2)
    -2e-15

    a value in the middle should be in the middle
    """
    m = Mutator()
    neutral = 0
    value = 1e-15
    m.setNeutral(neutral-neutral)
    m.addDelta(Location(pop=1), value-neutral, deltaName="test1")
    m.addDelta(Location(snap=1), -1*value-neutral, deltaName="test2")
    m.addDelta(Location(pop=1, snap=1), 0.5*value-neutral, punch=True, deltaName="test2")
    return m.getInstance(Location(pop=l, snap=n)) + neutral


def test_getLimits(a, b, t):
    """Test the getLimits function
    >>> test_getLimits(0, 1, 0)
    {'pop': (None, 0, None)}
    >>> test_getLimits(0, 1, 0.5)
    {'pop': (0, None, 1)}
    >>> test_getLimits(0, 1, 1)
    {'pop': (None, {1: [<Location pop:1 >]}, None)}
    """
    la = Location(pop=a)
    lb = Location(pop=b)
    locations = [la, lb]
    test  = Location(pop=t)
    print(getLimits(locations, test))


def test_methods():
    """ Test some of the methods.
    >>> m = test_methods()
    >>> sorted(list(m.getAxisNames()))
    ['pop', 'snap']
    """
    m = Mutator()
    neutral = 0
    value = 100.0
    m.setNeutral(neutral-neutral)
    m.addDelta(Location(pop=1), value-neutral, deltaName="test1")
    m.addDelta(Location(snap=1), -1*value-neutral, deltaName="test2")
    m.addDelta(Location(pop=1, snap=1), 50, punch=True, deltaName="test2")
    return m


def test_builder():
    """ Test the mutator builder.

    >>> items = [
    ...    (Location(pop=1, snap=1), 1),
    ...    (Location(pop=2, snap=1), 2),
    ...    (Location(pop=3, snap=1), 3),
    ...    (Location(pop=1, snap=2), 4),
    ...    (Location(pop=2, snap=2), 5),
    ...    (Location(pop=3, snap=2), 6),
    ... ]
    >>> bias, mb = buildMutator(items)
    >>> bias
    <Location pop:1, snap:1 >
    >>> mb.makeInstance(Location(pop=1, snap=1))
    1
    >>> mb.makeInstance(Location(pop=1, snap=2))
    4
    >>> mb.makeInstance(Location(pop=3, snap=2))
    6
    >>> mb.makeInstance(Location(pop=3, snap=1.5))
    4.5
    """


def test_builderBender_1():
    """ Test the mutator builder with a warp dict

    >>> items = [
    ...    (Location(pop=0), 0),
    ...    (Location(pop=10), 10),
    ... ]
    >>> axisdict = dict(pop = dict(name='pop', minimum=0, maximum=1000, default=0, map=[(0,0), (5, 2), (7, 7), (10,10)]))
    >>> bias, mb = buildMutator(items, axisdict)
    >>> bias
    <Location pop:0 >
    >>> sorted(mb.items())
    [((), (0, 'origin')), ((('pop', 10),), (10, None))]
    >>> mb.makeInstance(Location(pop=0), bend=True)
    0
    >>> mb.makeInstance(Location(pop=1), bend=True)
    0.4
    >>> mb.makeInstance(Location(pop=2), bend=True)
    0.8
    >>> mb.makeInstance(Location(pop=3), bend=True)
    1.2
    >>> mb.makeInstance(Location(pop=4), bend=True)
    1.6
    >>> mb.makeInstance(Location(pop=5), bend=True)
    2.0
    >>> mb.makeInstance(Location(pop=6), bend=True)
    4.5
    >>> mb.makeInstance(Location(pop=7), bend=True)
    7.0
    >>> mb.makeInstance(Location(pop=8), bend=True)
    7.999999999999999
    >>> mb.makeInstance(Location(pop=9), bend=True)
    9.0
    >>> mb.makeInstance(Location(pop=10), bend=True)
    10
    """


def test_builderBender_2():
    """ Test the mutator builder with a warp dict

    >>> items = [
    ...    (Location(pop=0), 0),
    ...    #(Location(pop=7), 5),
    ...    (Location(pop=10), 10),
    ... ]
    >>> axisdict = dict(pop = dict(name='pop', minimum=0, maximum=1000, default=0, map=[(0,0), (5, 2), (10,10)]))
    >>> bias, mb = buildMutator(items, axisdict)
    >>> bias
    <Location pop:0 >
    >>> sorted(mb.items())
    [((), (0, 'origin')), ((('pop', 10),), (10, None))]
    >>> mb.makeInstance(Location(pop=0), bend=True)
    0
    >>> r = []
    >>> for p in range(0, 11):
    ...     r.append(mb.makeInstance(Location(pop=p), bend=True))
    >>> r
    [0, 0.4, 0.8, 1.2, 1.6, 2.0, 3.5999999999999996, 5.2, 6.799999999999999, 8.4, 10]
    """


def test_builderBender_3():
    """
    Test case from
    https://github.com/googlefonts/fontmake/pull/552#issuecomment-493617252
    >>> masters = [
    ...     (Location(Width=70), 0),
    ...     (Location(Width=100), 100),
    ... ]
    >>> axes = {
    ...     'Width': {
    ...         'tag': 'wdth',
    ...         'name': 'Width',
    ...         'minimum': 62.5,
    ...         'default': 100.0,
    ...         'maximum': 100.0,
    ...         'map': [(62.5, 70.0), (75.0, 79.0), (87.5, 89.0), (100.0, 100.0)],
    ...     }
    ... }
    >>> _, mut = buildMutator(masters, axes)
    >>> mut.makeInstance(Location(Width=79), bend=False)
    30.0
    >>> mut.makeInstance(Location(Width=75), bend=True)
    30.0
    """


if __name__ == "__main__":
    import sys
    import doctest
    sys.exit(doctest.testmod().failed)
