from mutatorMath.objects.mutator import buildMutator
from mutatorMath.objects.location import Location

# source locations implicitly specified in internal, design location.
# the second item is master's value at given location. I use numbers for simplicity
# but it can be any object that supports addition and multiplication (fontMath objects)
masters = [
    (Location(Width=70), 0),
    (Location(Width=100), 100),
]

axes = {
    'Width': {
        'tag': 'wdth',
        'name': 'Width',
        # min/default/max are always in user-space coordinates
        'minimum': 62.5,
        'default': 100.0,
        'maximum': 100.0,
        # first item (input) is user-space coordinate, second item (output) is internal design coordinate
        'map': [(62.5, 70.0), (75.0, 79.0), (87.5, 89.0), (100.0, 100.0)],
        #'map': [(70.0, 62.5), (79.0, 75.0), (89.0, 87.5), (100.0, 100.0)],
    }
}

_, mut = buildMutator(masters, axes)

# instance locations are also specified in internal design coordinates (at least varLib assumes they are)
instance_location = Location(Width=79)

# the result is 27.642276422764223, but it should have been 30.0
print(mut.makeInstance(Location(Width=79), bend=False))
print(mut.makeInstance(Location(Width=75), bend=True))
print(mut.makeInstance(Location(Width=62.5), bend=True))
print(mut.makeInstance(Location(Width=100), bend=True))
