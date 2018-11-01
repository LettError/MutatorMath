# -*- coding: utf-8 -*-
from __future__ import print_function
from defcon.objects.font import Font
from fontMath import MathKerning

from fontMath.mathKerning import MathKerning

from mutatorMath.ufo.document import DesignSpaceDocumentWriter, DesignSpaceDocumentReader
from mutatorMath.objects.location import Location

import os, sys, shutil

"""

These are some basic tests for glyph geometry.

"""

def testingProgressFunc(state, action, text, tick):
    """ Progress function that gets passed to the DesignSpaceDocumentReader should
        report on the faulty kerning pairs it found.
    """
    pass

def addGlyphs(font, s):
    # we need to add the glyphs
    for n in ['glyphOne', 'glyphTwo']:
        font.newGlyph(n)
        g = font[n]
        p = g.getPen()
        p.moveTo((0,0))
        p.lineTo((s,0))
        p.lineTo((s,s))
        p.lineTo((0,s))
        p.closePath()
        g.width = s

def fillInfo(font):
    font.info.unitsPerEm = 1000
    font.info.ascender = 800
    font.info.descender = -200

def makeTestFonts(rootPath):
    """ Make some test fonts that have the kerning problem."""
    path1 = os.path.join(rootPath, "geometryMaster1.ufo")
    path2 = os.path.join(rootPath, "geometryMaster2.ufo")
    path3 = os.path.join(rootPath, "geometryInstance.ufo")
    path4 = os.path.join(rootPath, "geometryInstanceAnisotropic1.ufo")
    path5 = os.path.join(rootPath, "geometryInstanceAnisotropic2.ufo")

    # Two masters
    f1 = Font()
    addGlyphs(f1, 100)

    f2 = Font()
    addGlyphs(f2, 500)

    fillInfo(f1)
    fillInfo(f2)

    # save
    f1.save(path1, 2)
    f2.save(path2, 2)
    return path1, path2, path3, path4, path5


def testGeometry(rootPath, cleanUp=True):
    # that works, let's do it via MutatorMath
    path1, path2, path3, path4, path5 = makeTestFonts(rootPath)
    documentPath = os.path.join(rootPath, 'geometryTest.designspace')

    doc = DesignSpaceDocumentWriter(documentPath, verbose=True)
    doc.addSource(
            path1,
            name="master_1", 
            location=dict(width=0), 
            copyLib=True,
            copyGroups=True,
            copyInfo=True, 
            copyFeatures=True,
            )
    doc.addSource(
            path2,
            name="master_2", 
            location=dict(width=1000), 
            copyLib=False,
            copyGroups=False,
            copyInfo=False, 
            copyFeatures=False,
            )
    doc.startInstance(fileName=path3,
            familyName="TestInstance",
            styleName="Regular",
            location=dict(width=500)
            )
    doc.endInstance()
    doc.startInstance(fileName=path4,
            familyName="TestInstance",
            styleName="Anisotropic1",
            location=dict(width=(0, 1000))
            )
    doc.endInstance()
    doc.startInstance(fileName=path5,
            familyName="TestInstance",
            styleName="Anisotropic2",
            location=dict(width=(1000, 0))
            )
    doc.endInstance()
    doc.save()

    # execute the designspace.
    doc = DesignSpaceDocumentReader(documentPath, 2, roundGeometry=True, verbose=True, progressFunc=testingProgressFunc)
    doc.process(makeGlyphs=True, makeKerning=False, makeInfo=True)

    r1 = Font(path3)
    assert r1['glyphOne'].bounds == (0, 0, 300, 300)

    r2 = Font(path4)
    assert r2['glyphOne'].bounds == (0, 0, 100, 500)

    r3 = Font(path5)
    assert r3['glyphOne'].bounds == (0, 0, 500, 100)

    if cleanUp:
        # remove the mess
        os.remove(documentPath)
        shutil.rmtree(path1)
        shutil.rmtree(path2)
        shutil.rmtree(path3)
        shutil.rmtree(path4)
        shutil.rmtree(path5)

    return True


def test1():
    """
    >>> import time
    >>> import os
    >>> testData = os.path.join(os.path.dirname(__file__), "testData")
    >>> try:
    ...     os.mkdir(testData)
    ... except OSError:
    ...     pass
    >>> testGeometry(testData, cleanUp=False)
    True
    """


if __name__ == "__main__":
    import doctest
    sys.exit(doctest.testmod().failed)
