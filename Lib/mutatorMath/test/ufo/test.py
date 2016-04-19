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



if __name__ == "__main__":
    import sys
    import doctest
    def test1():
        """
        >>> import time
        >>> testRoot = os.path.join(os.getcwd(), 'data')
        >>> documentPath = os.path.join(testRoot, 'exporttest_basic.designspace')
        >>> sourcePath = os.path.join(testRoot, 'sources')
        >>> instancePath = os.path.join(testRoot, 'instances')
        >>> master1Path = os.path.join(testRoot, )
        >>> logPath = os.path.join(testRoot, "tests.log")
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
        ...        mutedGlyphNames=['a',] )
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
        >>> doc.writeGlyph("M", unicodeValue=0xff, location=dict(width=0.9), masters=None, note="testnote123")
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
        >>> fontObj, loc = doc.sources['master_2']
        >>> loc.asTuple()
        (('width', 1.0),)

            # check the instances
        >>> assert os.path.basename(testOutputFileName) in doc.results
        >>> resultUFOPath = doc.results[os.path.basename(testOutputFileName)]
        >>> instance = defcon.objects.font.Font(resultUFOPath)
            
            # note: the next assertion will fail if the calculations were made with the 
            # pre-ufo3 fontMath.

        >>> assert instance['M'].unicode == 0xff

            # check the groups
        >>> instance.groups.items()
        [('testGroup', ['E', 'F', 'H'])]

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
        >>> doc.writeKerning(location=dict(weight=1))
        >>> doc.endInstance()
        >>> doc.save()
        >>> doc = DesignSpaceDocumentReader(documentPath, ufoVersion, roundGeometry=roundGeometry, verbose=True, logPath=logPath)
        >>> doc.process(makeGlyphs=False, makeKerning=True, makeInfo=False)
        >>> assert os.path.basename(testOutputFileName) in doc.results
        >>> resultUFOPath = doc.results[os.path.basename(testOutputFileName)]
        >>> instance = defcon.objects.font.Font(resultUFOPath)
        >>> assert instance.kerning.items() == [(('@MMK_L_A', 'V'), 100), (('V', '@MMK_R_A'), 100)]


            # test the effects of muting the kerning
        >>> documentPath = os.path.join(testRoot, 'exporttest_kerning_muted.designspace')
        >>> doc = DesignSpaceDocumentWriter(documentPath, verbose=False)
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
        >>> doc = DesignSpaceDocumentReader(documentPath, ufoVersion, roundGeometry=roundGeometry, verbose=False, logPath=logPath)
        >>> paths = doc.getSourcePaths()
        >>> len(paths)
        2
        >>> doc.process(makeGlyphs=False, makeKerning=True, makeInfo=False)
        >>> assert doc.groupsSource == 'master_1'
        >>> assert os.path.basename(testOutputFileName) in doc.results
        >>> resultUFOPath = doc.results[os.path.basename(testOutputFileName)]
        >>> instance = defcon.objects.font.Font(resultUFOPath)

            # the bold condensed kerning master has been muted, we expect the light condensed data in the instance
        >>> assert instance.kerning.items() == [(('@MMK_L_A', 'V'), -100), (('V', '@MMK_R_A'), -100)]


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
        >>> assert instance.info.openTypeOS2VendorID == "ADBE"
        >>> assert instance.info.copyright == "Copyright-token-string"



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
        >>> here = os.path.join(os.getcwd(), 'data', 'exporttest_basic.designspace')
        >>> results = build(here, outputUFOFormatVersion=2)
        >>> ufoFullPath = results[0]['testOutput_glyphs.ufo']
        >>> ufoRelPath = ufoFullPath.replace(os.getcwd(), '')
        >>> ufoRelPath
        '/data/instances/A/testOutput_glyphs.ufo'

        """

    sys.exit(doctest.testmod().failed)
