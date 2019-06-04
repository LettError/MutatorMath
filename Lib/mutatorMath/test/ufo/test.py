# -*- coding: utf-8 -*-
from __future__ import print_function

"""

    These are tests for writing and processing designspace.designspace documents
        - write various designspaces
        - read them
        - process them using the test fonts
        - show masters can be read from different directories
        - show instances can be generated into different directories
        - do some basic output testing.
    

"""

import os

import defcon.objects.font
import mutatorMath.objects.error

from mutatorMath.ufo.document import DesignSpaceDocumentWriter, DesignSpaceDocumentReader
from mutatorMath.objects.location import Location

def stripPrefix(d):
    # strip the "public.kern" prefixes from d
    new = []
    for pair, value in d:
        a, b = pair
        if "public.kern" in a:
            a = a[13:]
        if "public.kern" in b:
            b = b[13:]
        new.append(((a,b), value))
    return sorted(new)

#t = [(('V', 'public.kern2.@MMK_R_A'), -100), (('public.kern1.@MMK_L_A', 'V'), -100)]
#stripPrefix(t)


def test1():
    """
    >>> import time
    >>> from mutatorMath.ufo.document import initializeLogger
    >>> testRoot = os.path.join(os.path.dirname(__file__), 'data')
    >>> documentPath = os.path.join(testRoot, 'exporttest_basic.designspace')
    >>> sourcePath = os.path.join(testRoot, 'sources')
    >>> instancePath = os.path.join(testRoot, 'instances')
    >>> master1Path = os.path.join(testRoot, )
    >>> #logPath = None # 
    >>> logPath = os.path.join(testRoot, "tests.log")
    >>> if logPath is not None:
    ...     if os.path.exists(logPath):
    ...         os.remove(logPath)
    ...     initializeLogger(logPath)
    >>> ufoVersion=2
    >>> roundGeometry=True      # this will trigger some fails if run with a pre-ufo3 fontMath.

    >>> doc = DesignSpaceDocumentWriter(documentPath, verbose=True)
    >>> doc.addSource(
    ...        os.path.join(sourcePath, "light", "LightCondensed.ufo"),
    ...        name="master_1", 
    ...        location=dict(width=0), 
    ...        copyLib=True,            # change to see the copy Lib test fail
    ...        copyGroups=True,         # change to see assertions fail on groupSource and instance groups.
    ...        copyInfo=True, 
    ...        copyFeatures=True,
    ...        muteKerning=False, 
    ...        muteInfo=True,
    ...        mutedGlyphNames=['a',],
    ...        familyName="ExplicitSourceFamilyName",
    ...        styleName="ExplicitSourceStyleName",)
    >>> doc.addSource(
    ...        os.path.join(sourcePath, "light", "LightWide.ufo"),
    ...        name="master_2", 
    ...        location=dict(width=1), 
    ...        copyLib=False, 
    ...        copyGroups=False, 
    ...        copyInfo=False, 
    ...        muteKerning=True, 
    ...        muteInfo=True,
    ...        mutedGlyphNames=['b'] )
    >>> testOutputFileName = os.path.join(instancePath, "A", "testOutput_glyphs.ufo")
    >>> glyphMasters = [('M', "master_1", dict(width=0)), ('M', "master_2", dict(width=1)), ]
    >>> doc.startInstance(fileName=testOutputFileName,
    ...       familyName="TestFamily",
    ...       styleName="TestStyleName",
    ...       location=dict(width=(0.2, 0.8)))
    >>> doc.writeGlyph("M", unicodes=[0xff], location=dict(width=0.9), masters=None, note="testnote123")
    >>> doc.writeGlyph("N", location=dict(width=0.7), masters=glyphMasters)
    >>> doc.endInstance()
    >>> doc.save()
    >>> doc = DesignSpaceDocumentReader(documentPath, ufoVersion, roundGeometry=roundGeometry, verbose=True, logPath=logPath)
    >>> doc.process(makeGlyphs=True, makeKerning=False, makeInfo=False)

        # check if we found the UFOs
    >>> assert "master_1" in doc.sources
    >>> assert "master_2" in doc.sources

        # check if we are reading the muting flags
    >>> assert doc.libSource == 'master_1'
    >>> assert doc.groupsSource == 'master_1'
    >>> assert doc.libSource == 'master_1'
    >>> assert doc.muted == {'info': ['master_1', 'master_2'], 'glyphs': {'master_2': ['b'], 'master_1': ['a']}, 'kerning': ['master_2']}

        # check the locations
    >>> fontObj, loc = doc.sources['master_1']
    >>> loc.asTuple()
    (('width', 0.0),)
    >>> loc.asTuple()
    (('width', 0.0),)
    >>> fontObj, loc = doc.sources['master_2']
    >>> loc.asTuple()
    (('width', 1.0),)

        # check the instances
    >>> assert os.path.basename(testOutputFileName) in doc.results
    >>> resultUFOPath = doc.results[os.path.basename(testOutputFileName)]
    >>> instance = defcon.objects.font.Font(resultUFOPath)

        # note: the next assertion will fail if the calculations were made with the
        # pre-ufo3 fontMath.

    >>> assert instance['M'].unicodes == [0xff]

        # check the groups
    >>> ('testGroup', ['E', 'F', 'H']) in list(instance.groups.items())
    True

        # check the lib
    >>> assert "testLibItemKey" in instance.lib.keys()

        # check the feature text was copied from the source
    >>> assert "Hi_this_is_the_feature." in instance.features.text

        # basic kerning processing.
    >>> documentPath = os.path.join(testRoot, 'exporttest_kerning.designspace')
    >>> doc = DesignSpaceDocumentWriter(documentPath, verbose=True)
    >>> doc.addSource(
    ...        os.path.join(sourcePath, "light", "LightCondensed.ufo"),
    ...        name="master_1",
    ...        location=dict(weight=0),
    ...        copyLib=True,
    ...        copyGroups=True,
    ...        copyInfo=True,
    ...        muteKerning=False,
    ...        muteInfo=False)
    >>> doc.addSource(
    ...        os.path.join(sourcePath, "bold", "BoldCondensed.ufo"),
    ...        name="master_2",
    ...        location=dict(weight=1),
    ...        copyLib=False,
    ...        copyGroups=False,
    ...        copyInfo=False,
    ...        muteKerning=False,
    ...        muteInfo=False )
    >>> testOutputFileName = os.path.join(instancePath, "B", "testOutput_kerning.ufo")
    >>> doc.startInstance(fileName=testOutputFileName, familyName="TestFamily", styleName="TestStyleName", location=dict(weight=0.6))

        # give this kerning master a different location
    >>> #doc.writeKerning(location=dict(weight=1))
    >>> #doc.endInstance()
    >>> #doc.save()
    >>> #doc = DesignSpaceDocumentReader(documentPath, ufoVersion, roundGeometry=roundGeometry, verbose=True, logPath=logPath)
    >>> #doc.process(makeGlyphs=False, makeKerning=True, makeInfo=False)
    >>> #assert os.path.basename(testOutputFileName) in doc.results
    >>> #resultUFOPath = doc.results[os.path.basename(testOutputFileName)]
    >>> #instance = defcon.objects.font.Font(resultUFOPath)
    >>> #assert sorted(instance.kerning.items()) == stripPrefix([(('@MMK_L_A', 'V'), 100), (('V', '@MMK_R_A'), 100)])


        # test the effects of muting the kerning
    >>> documentPath = os.path.join(testRoot, 'exporttest_kerning_muted.designspace')
    >>> doc = DesignSpaceDocumentWriter(documentPath, verbose=True)
    >>> doc.addSource(
    ...        os.path.join(sourcePath, "light", "LightCondensed.ufo"),
    ...        name="master_1",
    ...        location=dict(weight=0),
    ...        copyLib=True,
    ...        copyGroups=True,
    ...        copyInfo=True,
    ...        muteKerning=False,
    ...        muteInfo=False)
    >>> doc.addSource(
    ...        os.path.join(sourcePath, "bold", "BoldCondensed.ufo"),
    ...        name="master_2",
    ...        location=dict(weight=1),
    ...        copyLib=False,
    ...        copyGroups=False,
    ...        copyInfo=False,
    ...        muteKerning=True,    # mute a master at a non-origin location!
    ...        muteInfo=False )
    >>> testOutputFileName = os.path.join(instancePath, "C", "testOutput_kerning_muted.ufo")
    >>> testLocation = dict(weight=0.6)        # change this location to see calculation assertions fail.
    >>> doc.startInstance(fileName=testOutputFileName, familyName="TestFamily", styleName="TestStyleName", location=testLocation)
    >>> doc.writeKerning()
    >>> doc.endInstance()
    >>> doc.save()
    >>> doc = DesignSpaceDocumentReader(documentPath, ufoVersion, roundGeometry=roundGeometry, verbose=True, logPath=logPath)
    >>> paths = doc.getSourcePaths()
    >>> len(paths)
    2
    >>> doc.process(makeGlyphs=False, makeKerning=True, makeInfo=False)
    >>> assert doc.groupsSource == 'master_1'
    >>> assert os.path.basename(testOutputFileName) in doc.results
    >>> resultUFOPath = doc.results[os.path.basename(testOutputFileName)]
    >>> instance = defcon.objects.font.Font(resultUFOPath)

        # the bold condensed kerning master has been muted, we expect the light condensed data in the instance    
    >>> assert [(('@MMK_L_A', 'V'), -100), (('V', '@MMK_R_A'), -100)] == stripPrefix(sorted(instance.kerning.items()))

        # info data
        #   calculating fields
        #   copying fields
    >>> documentPath = os.path.join(testRoot, 'exporttest_info.designspace')
    >>> doc = DesignSpaceDocumentWriter(documentPath, verbose=True)
    >>> doc.addSource(
    ...        os.path.join(sourcePath, "light", "LightCondensed.ufo"),
    ...        name="master_1",
    ...        location=dict(weight=0),
    ...        copyLib=False,
    ...        copyGroups=False,
    ...        copyInfo=True,       # flip to False and see some assertions fail
    ...        muteKerning=True,
    ...        muteInfo=False)
    >>> doc.addSource(
    ...        os.path.join(sourcePath, "bold", "BoldCondensed.ufo"),
    ...        name="master_2",
    ...        location=dict(weight=1),
    ...        copyLib=False,
    ...        copyGroups=False,
    ...        copyInfo=False,
    ...        muteKerning=True,
    ...        muteInfo=False )
    >>> testOutputFileName = os.path.join(instancePath, "D", "testOutput_info.ufo")
    >>> testLocation = dict(weight=0.5)       # change this location to see calculation assertions fail.
    >>> doc.startInstance(
    ...        fileName=testOutputFileName,
    ...        familyName="TestFamily",
    ...        styleName="TestStyleName",
    ...        location=testLocation,
    ...        postScriptFontName="TestPostScriptFontNameValue",
    ...        styleMapFamilyName="TestStyleMapFamilyNameValue",
    ...        styleMapStyleName="bold italic",
    ...        )
    >>> doc.writeInfo()
    >>> doc.endInstance()
    >>> doc.save()
    >>> doc = DesignSpaceDocumentReader(documentPath, ufoVersion, roundGeometry=roundGeometry, verbose=True, logPath=logPath)
    >>> doc.process(makeGlyphs=False, makeKerning=False, makeInfo=True)

    >>> assert os.path.basename(testOutputFileName) in doc.results
    >>> resultUFOPath = doc.results[os.path.basename(testOutputFileName)]
    >>> instance = defcon.objects.font.Font(resultUFOPath)

        # example calculated values
    >>> assert instance.info.ascender == 750
    >>> assert instance.info.capHeight == 750

        # example copied values
    >>> assert instance.info.versionMajor == 1
    >>> assert instance.info.openTypeOS2VendorID == "LTTR"
    >>> assert instance.info.copyright == "License same as MutatorMath. BSD 3-clause. [test-token: C]"

        # test the build script
    >>> documentPath = os.path.join(testRoot, 'exporttest_build.designspace')
    >>> doc = DesignSpaceDocumentWriter(documentPath, verbose=True)
    >>> doc.addSource(
    ...        os.path.join(sourcePath, "light", "LightCondensed.ufo"),
    ...        name="master_1",
    ...        location=dict(weight=0),
    ...        copyLib=True,
    ...        copyGroups=True,
    ...        copyInfo=True,
    ...        muteKerning=False,
    ...        muteInfo=False)
    >>> doc.addSource(
    ...        os.path.join(sourcePath, "bold", "BoldCondensed.ufo"),
    ...        name="master_2",
    ...        location=dict(weight=1),
    ...        copyLib=False,
    ...        copyGroups=False,
    ...        copyInfo=False,
    ...        muteKerning=False,
    ...        muteInfo=False )
    >>> testOutputFileName = os.path.join(instancePath, "E", "testOutput_build.ufo")
    >>> testLocation = dict(weight=0.25)       # change this location to see calculation assertions fail.
    >>> doc.startInstance(
    ...        fileName=testOutputFileName,
    ...        familyName="TestFamily",
    ...        styleName="TestStyleName",
    ...        location=testLocation)
    >>> doc.writeInfo()
    >>> doc.writeKerning()
    >>> doc.endInstance()
    >>> doc.save()

        # test build function -- single designspace file
    >>> from mutatorMath.ufo import build
    >>> import os
    >>> import posixpath
    >>> here = os.path.join(os.path.dirname(__file__), 'data', 'exporttest_basic.designspace')
    >>> results = build(here, outputUFOFormatVersion=2)
    >>> ufoFullPath = results[0]['testOutput_glyphs.ufo']
    >>> ufoRelPath = os.path.relpath(ufoFullPath, os.path.dirname(__file__))
    >>> posixRelPath = posixpath.join(*ufoRelPath.split(os.path.sep))
    >>> posixRelPath
    'data/instances/A/testOutput_glyphs.ufo'

    # test the axes elements
    >>> documentPath = os.path.join(testRoot, 'warpmap_test.designspace')
    >>> doc = DesignSpaceDocumentWriter(documentPath, verbose=True)
    >>> def grow(base, factor, steps):
    ...     return [(i*100, int(round(base*(1+factor)**i))) for i in range(steps)]
    >>> doc.addAxis("wght", "weight", 0, 1000, 0, grow(100,0.55,11))
    >>> doc.addSource(
    ...        os.path.join(sourcePath, "stems", "StemThin.ufo"),
    ...        name="master_1",
    ...        location=dict(weight=0),
    ...        copyLib=True,
    ...        copyGroups=True,
    ...        copyInfo=True,
    ...        muteKerning=False,
    ...        muteInfo=False)
    >>> doc.addSource(
    ...        os.path.join(sourcePath, "stems", "StemBold.ufo"),
    ...        name="master_2",
    ...        location=dict(weight=1000),
    ...        copyLib=False,
    ...        copyGroups=False,
    ...        copyInfo=False,
    ...        muteKerning=False,
    ...        muteInfo=False )
    >>> testOutputFileName = os.path.join(instancePath, "W", "StemOutput.ufo")
    >>> testLocation = dict(weight=0)       # change this location to see calculation assertions fail.
    >>> doc.startInstance(
    ...        fileName=testOutputFileName,
    ...        familyName="TestFamily",
    ...        styleName="Warped",
    ...        location=testLocation)
    >>> doc.writeInfo()
    >>> doc.writeKerning()
    >>> glyphMasters = [('I', "master_1", dict(weight=0)), ('I', "master_2", dict(weight=1000)), ]
    >>> for i in range(0, 1000, 50):
    ...    doc.writeGlyph("I.%04d"%i, location=dict(weight=i), masters=glyphMasters)
    ...
    >>> doc.endInstance()
    >>> doc.save()

    >>> doc = DesignSpaceDocumentReader(documentPath, ufoVersion, roundGeometry=roundGeometry, verbose=True, logPath=logPath)
    >>> doc.process(makeGlyphs=True, makeKerning=False, makeInfo=False)

    >>> documentPath = os.path.join(testRoot, 'no_warpmap_test.designspace')
    >>> doc = DesignSpaceDocumentWriter(documentPath, verbose=True)
    >>> doc.addAxis("wght", "weight", 0, 1000, 0)
    >>> doc.addSource(
    ...        os.path.join(sourcePath, "stems", "StemThin.ufo"),
    ...        name="master_1",
    ...        location=dict(weight=0),
    ...        copyLib=True,
    ...        copyGroups=True,
    ...        copyInfo=True,
    ...        muteKerning=False,
    ...        muteInfo=False)
    >>> doc.addSource(
    ...        os.path.join(sourcePath, "stems", "StemBold.ufo"),
    ...        name="master_2",
    ...        location=dict(weight=1000),
    ...        copyLib=False,
    ...        copyGroups=False,
    ...        copyInfo=False,
    ...        muteKerning=False,
    ...        muteInfo=False )
    >>> testOutputFileName = os.path.join(instancePath, "W", "StemOutput_nowarp.ufo")
    >>> testLocation = dict(weight=0)       # change this location to see calculation assertions fail.
    >>> doc.startInstance(
    ...        fileName=testOutputFileName,
    ...        familyName="TestFamily",
    ...        styleName="NotWarped",
    ...        location=testLocation)
    >>> doc.writeInfo()
    >>> doc.writeKerning()
    >>> glyphMasters = [('I', "master_1", dict(weight=0)), ('I', "master_2", dict(weight=1000)), ]
    >>> for i in range(0, 1000, 50):
    ...    doc.writeGlyph("I.%04d"%i, location=dict(weight=i), masters=glyphMasters)
    ...
    >>> doc.endInstance()
    >>> doc.save()


    >>> doc = DesignSpaceDocumentReader(documentPath, ufoVersion, roundGeometry=roundGeometry, verbose=True, logPath=logPath)
    >>> doc.process(makeGlyphs=True, makeKerning=False, makeInfo=False)

    # test the axes element
    >>> from pprint import pprint
    >>> documentPath = os.path.join(testRoot, 'axes_test.designspace')
    >>> doc = DesignSpaceDocumentWriter(documentPath, verbose=True)
    >>> def grow(base, factor, steps):
    ...     return [(i*100, int(round(base*(1+factor)**i))) for i in range(steps)]

    >>> # axis with a warp map
    >>> warpMap = grow(100,0.55,11)
    >>> doc.addAxis("wght", "weight", -1000, 1000, 0, warpMap)
    >>> # axis without a warp map
    >>> doc.addAxis("wdth", "width", 0, 1000, 0)
    >>> doc.save()

    >>> doc = DesignSpaceDocumentReader(documentPath, ufoVersion, roundGeometry=roundGeometry, verbose=True, logPath=logPath)
    >>> pprint(doc.axes)
    {'weight': {'default': 0.0,
                'map': [(0.0, 100.0),
                        (100.0, 155.0),
                        (200.0, 240.0),
                        (300.0, 372.0),
                        (400.0, 577.0),
                        (500.0, 895.0),
                        (600.0, 1387.0),
                        (700.0, 2149.0),
                        (800.0, 3332.0),
                        (900.0, 5164.0),
                        (1000.0, 8004.0)],
                'maximum': 1000.0,
                'minimum': -1000.0,
                'name': 'weight',
                'tag': 'wght'},
     'width': {'default': 0.0,
               'map': [],
               'maximum': 1000.0,
               'minimum': 0.0,
               'name': 'width',
               'tag': 'wdth'}}

    >>> doc.process(makeGlyphs=False, makeKerning=False, makeInfo=False)
    """

def bender_and_mutatorTest():
    """
    >>> from mutatorMath.objects.bender import Bender
    >>> from mutatorMath.objects.location import Location
    >>> from mutatorMath.objects.mutator import buildMutator

    >>> w = {'aaaa':{
    ...     'map': [(300, 50),
    ...          (400, 100),
    ...          (700, 150)],
    ...     'name':'aaaaAxis',
    ...     'tag':'aaaa',
    ...     'minimum':0,
    ...     'maximum':1000,
    ...     'default':0}}

    >>> b = Bender(w)
    >>> assert b(dict(aaaa=300)) == {'aaaa': 50}
    >>> assert b(dict(aaaa=400)) == {'aaaa': 100}
    >>> assert b(dict(aaaa=700)) == {'aaaa': 150}

    master locations are always in internal design coordinates, thus they are
    considered to be already mapped or bent.

    >>> items = [
    ...     (Location(aaaa=50), 0),
    ...     (Location(aaaa=100), 50),
    ...     (Location(aaaa=150), 100),
    ... ]

    >>> bias, mut = buildMutator(items, w, bias=Location(aaaa=100))
    >>> bias
    <Location aaaa:100 >

    >>> bias, mut = buildMutator(items, w, bias=Location(aaaa=150))
    >>> bias
    <Location aaaa:150 >

    >>> bias, mut = buildMutator(items, w, bias=Location(aaaa=50))
    >>> bias
    <Location aaaa:50 >

    >>> expect = sorted([(('aaaa', 100),), (('aaaa', 50),), ()])
    >>> expect
    [(), (('aaaa', 50),), (('aaaa', 100),)]

    >>> got = sorted(mut.keys())
    >>> got
    [(), (('aaaa', 50),), (('aaaa', 100),)]

    >>> assert got == expect

    Instance location are not bent by default, i.e. are interpreted as internal
    design coordinates:
    >>> assert mut.makeInstance(Location(aaaa=50)) == 0
    >>> assert mut.makeInstance(Location(aaaa=100)) == 50
    >>> assert mut.makeInstance(Location(aaaa=150)) == 100

    If bend=True, instance locations are interpreted as user-space coordinates
    >>> assert mut.makeInstance(Location(aaaa=300), bend=True) == 0
    >>> assert mut.makeInstance(Location(aaaa=400), bend=True) == 50
    >>> assert mut.makeInstance(Location(aaaa=700), bend=True) == 100
    """

if __name__ == '__main__':
    import sys
    import doctest
    sys.exit(doctest.testmod().failed)
