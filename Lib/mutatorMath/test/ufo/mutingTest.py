# -*- coding: utf-8 -*-
from __future__ import print_function
from defcon.objects.font import Font
from fontMath import MathKerning

from fontMath.mathKerning import MathKerning

from mutatorMath.ufo.document import DesignSpaceDocumentWriter, DesignSpaceDocumentReader
from mutatorMath.objects.location import Location

import os, sys, shutil

"""

    This is a test for the muting functionality.

    - mute masters
    - mute specific glyphs

"""

def testingProgressFunc(state, action, text, tick):
    """ Progress function that gets passed to the DesignSpaceDocumentReader should
        report on the faulty kerning pairs it found.
    """
    pass
    #print "testingProgressFunc", state, action, text, tick


def addGlyphs(font, offset=0):
    # we need to add the glyphs
    # add an offset so we can see if the masters are active.
    for n in ['glyphOne', 'glyphTwo', 'glyphThree', 'glyphFour']:
        font.newGlyph(n)
        g = font[n]
        p = g.getPen()
        p.moveTo((100+offset,100+offset))
        p.lineTo((200+offset,200+offset))
        p.lineTo((offset,100+offset))
        p.closePath()

def makeTestFonts(rootPath):
    """ Make some test fonts that have the kerning problem."""
    path1 = os.path.join(rootPath, "mutingMaster1.ufo")
    path2 = os.path.join(rootPath, "mutingMaster2.ufo")
    path3 = os.path.join(rootPath, "mutedGlyphInstance.ufo")
    # Two masters
    f1 = Font()
    addGlyphs(f1, 0)
    f1.info.unitsPerEm = 1000
    f1.kerning[('glyphOne', 'glyphOne')] = -100
    f2 = Font()
    addGlyphs(f2, 33)
    f2.info.unitsPerEm = 2000
    f2.kerning[('glyphOne', 'glyphOne')] = -200
    # save
    f1.save(path1, 3)
    f2.save(path2, 3)
    return path1, path2, path3

def testMutingOptions(rootPath, cleanUp=True):
    # that works, let's do it via MutatorMath
    # path1 and path2 are masters. path3 is the instance
    path1, path2, path3 = makeTestFonts(rootPath)
    documentPath = os.path.join(rootPath, 'mutingTest.designspace')

    doc = DesignSpaceDocumentWriter(documentPath, verbose=True)
    doc.addSource(
            path1,
            name="master_1", 
            location=dict(width=0), 
            copyLib=True,
            copyGroups=True,
            copyInfo=True, 
            copyFeatures=True,
            muteKerning=True
            )
    doc.addSource(
            path2,
            name="master_2", 
            location=dict(width=1000), 
            copyLib=False,
            copyGroups=False,
            copyInfo=False, 
            copyFeatures=False,
            muteInfo=True,
            mutedGlyphNames=['glyphThree']  # mute glyphThree in master 1
            )
    doc.startInstance(fileName=path3,
            familyName="TestInstance",
            styleName="Regular",
            location=dict(width=500)
            )
    doc.writeGlyph('glyphFour', mute=True)  # mute glyphFour in the instance
    doc.writeKerning()
    doc.writeInfo()
    doc.endInstance()
    doc.save()

    # execute the designspace. 
    doc = DesignSpaceDocumentReader(documentPath, 2, roundGeometry=True, verbose=True, progressFunc=testingProgressFunc)
    doc.process(makeGlyphs=True, makeKerning=True, makeInfo=True)

    # look at the results
    m1 = Font(path1)
    m2 = Font(path2)
    r = Font(path3)
    # 
    # the glyphThree master was muted in the second master
    # so the instance glyphThree should be the same as the first master:
    assert r['glyphThree'].bounds == m1['glyphThree'].bounds
    # we muted glyphFour in the instance.
    # so it should not be part of the instance UFO:
    assert "glyphFour" not in r
    # font.info is muted for master2, so the instance has to have the values from master 1
    assert r.info.unitsPerEm == m1.info.unitsPerEm
    # kerning is muted for master1, so the instance has to have the kerning from master 2
    assert r.kerning[('glyphOne', 'glyphOne')] == m2.kerning[('glyphOne', 'glyphOne')]

    if cleanUp:
        # remove the mess
        try:
            os.remove(documentPath)
            shutil.rmtree(path1)
            shutil.rmtree(path2)
            shutil.rmtree(path3)
        except:
            pass

    return True


def test1():
    """
    >>> import time
    >>> import os
    >>> testData = os.path.join(os.path.dirname(__file__), "testData")
    >>> testMutingOptions(testData, cleanUp=False)
    True
    """

if __name__ == "__main__":
    import doctest
    sys.exit(doctest.testmod().failed)
