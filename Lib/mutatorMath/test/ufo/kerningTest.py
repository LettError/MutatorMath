# -*- coding: utf-8 -*-
from __future__ import print_function
from defcon.objects.font import Font
from fontMath import MathKerning

#from ufoLib.validators import kerningValidatorReportPairs
from fontMath.mathKerning import MathKerning

from mutatorMath.ufo.document import DesignSpaceDocumentWriter, DesignSpaceDocumentReader
from mutatorMath.objects.location import Location

import os, sys, shutil

"""

This is a test for a very specific problem that can occur
when two or more masters have valid kerning and groups,
but interpolations receive exceptions from both masters.
These exceptions can be in conflict.
It is hard to predict these conflicts exclusively on the input.
But they are easy to detect using the kerning validator from
ufoLib.

20160425 Changes in the validation of kerning in Defcon made this test irrelevant.
"""

def addGlyphs(font):
    # we need to add the glyphs
    for n in ['glyphOne', 'glyphTwo', 'glyphThree', 'glyphFour']:
        font.newGlyph(n)
        g = font[n]
        p = g.getPen()
        p.moveTo((100,100))
        p.lineTo((200,200))
        p.lineTo((0,100))
        p.closePath()

def makeTestFonts(rootPath):
    """ Make some test fonts that have the kerning problem."""
    path1 = os.path.join(rootPath, "validMaster1.ufo")
    path2 = os.path.join(rootPath, "validMaster2.ufo")
    path3 = os.path.join(rootPath, "invalidInstance.ufo")

    # Two masters
    f1 = Font()
    f1.groups['public.kern1.@MMK_L_one'] = ['glyphOne', 'glyphTwo']
    f1.groups['public.kern2.@MMK_R_two'] = ['glyphThree', 'glyphFour']
    addGlyphs(f1)

    f2 = Font()
    f2.groups.update(f1.groups)
    # both masters have the same groups

    addGlyphs(f2)
    assert f1.groups == f2.groups

    # a normal group / group pair in each master
    f1.kerning[('public.kern1.@MMK_L_one', 'public.kern2.@MMK_R_two')] = 1000
    f1.kerning[('a', 'b')] = 10
    f2.kerning[('public.kern1.@MMK_L_one', 'public.kern2.@MMK_R_two')] = 2000
    f2.kerning[('a', 'b')] = 10

    # a valid exception to this pair in each master
    f1.kerning[('public.kern1.@MMK_L_one', 'glyphThree')] = -500
    f2.kerning[('glyphOne', 'public.kern2.@MMK_R_two')] = -800

    # make sure the kerning and groups in each master validate.
    #assert kerningValidatorReportPairs(f1.kerning, f1.groups) == (True, [], [])
    #assert kerningValidatorReportPairs(f2.kerning, f2.groups) == (True, [], [])

    # save
    f1.save(path1, 3)
    f2.save(path2, 3)
    return path1, path2, path3

def testingProgressFunc(state, action, text, tick):
    """ Progress function that gets passed to the DesignSpaceDocumentReader should
        report on the faulty kerning pairs it found.
    """
    failPair1 = "invalidInstance.ufo:\nThese kerning pairs failed validation and have been removed:\nglyphOne, public.kern2.@MMK_R_two (-400) conflicts with public.kern1.@MMK_L_one, glyphThree (-250)\npublic.kern1.@MMK_L_one, glyphThree (-250) conflicts with glyphOne, public.kern2.@MMK_R_two (-400)"
    if state == "error" and action == 'kerning':
        assert failPair1 in text

def testOuroborosKerning(rootPath, cleanUp=True):
    # that works, let's do it via MutatorMath
    path1, path2, path3 = makeTestFonts(rootPath)
    documentPath = os.path.join(rootPath, 'kerningTest.designspace')

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
            location=dict(width=100)
            )
    doc.writeKerning(location=dict(width=500))
    doc.endInstance()
    doc.save()

    # execute the designspace. Kerning errors should be tripped by the 
    doc = DesignSpaceDocumentReader(documentPath, 2, roundGeometry=True, verbose=True, progressFunc=testingProgressFunc)
    doc.process(makeGlyphs=True, makeKerning=True, makeInfo=True)

    if cleanUp:
        # remove the mess
        shutil.rmtree(path1)
        shutil.rmtree(path2)
        shutil.rmtree(path3)

    return True


    def test1():
        """
        >>> import time
        >>> import os
        >>> testOuroborosKerning(os.path.join(os.getcwd(), "testData"), cleanUp=True)
        True
        """


if __name__ == "__main__":
    import doctest
    sys.exit(doctest.testmod().failed)
