"""

Test the kerning swap made by this script:
    mutatorMath/ufo/swap.py

This test makes a dictionary with the "drawings" of every pair of glyphs as the key (NSBezierPaths for 
each glyph in the sequence), and the glyph names and their kerning value as the pair. 

Then, it compares the same "drawings" of every pair from the destination font to test for:
    - Do these two glyph drawings ever show up in the Source font, even if they had different glyph names?
    - If these two glyph drawings do show up, did they have the same kerning value in that font?

"""


def compileFont(f):
    # Compile to an OTF and open as a Compositor font
    path = tempfile.mkstemp()[1]
    compiler = EmptyOTFCompiler()
    options = FontCompilerOptions()
    options.outputPath = path
    reports = compiler.compile(f.naked(), options)
    # Load the compiled font
    if os.path.exists(path) and reports["makeotf"] is not None and "makeotfexe [FATAL]" not in reports["makeotf"]:
        cFont = CFont(path)
        compileError = False
    else:
        cFont = None
        compileError = reports["makeotf"]
    os.remove(path)
    return cFont
    
    
def testAllGlyphs(font, cFont, glyphList):
    # Test all combinations of glyphs.
    # Use Compositor to find the kern value of a pair of glyphs.
    # Save a hash of the glyph outline digest, along with the pair of glyph names and the kern value.
    # This way, we can make sure that the art representing this pair of glyphs exists in another font and that its kern value matches.
    allPairs = {}
    if cFont:
        for pair0 in glyphList:
            for pair1 in glyphList:
                glyphRecords = cFont.process([pair0, pair1])
                kern = glyphRecords[0].xAdvance
                # Hash the outlines
                m = md5.new()
                for record in glyphRecords:
                    glyph = font[record.glyphName]
                    path = glyph.naked().getRepresentation("defconAppKit.NSBezierPath")
                    path = string.join(string.split(str(path), "\n")[1:]) # Lazy way to remove the first line containing the memory location
                    m.update(str(path))
                allPairs[m.digest()] = [(pair0, pair1), kern]
    return allPairs




if __name__ == "__main__":
    from fontCompiler.emptyCompiler import EmptyOTFCompiler
    from fontCompiler.compiler import FontCompilerOptions
    from compositor import Font as CFont
    import string
    import tempfile
    import os
    import md5

    root = os.getcwd()
    srcPath = os.path.join(root, "data", "sources", "swap", "Swap.ufo")
    dstPath = os.path.join(root, "data", "instances", "S", "SwapTestOutput.ufo")
    
    # Compare with the broken instance where the art of the "o" and one kerning pair changed:
    #dstPath = os.path.join(root, "data", "instances", "S", "SwapTestOutput-Broken.ufo")
    
    fSrc = OpenFont(srcPath, showUI=False)
    fDst = OpenFont(dstPath, showUI=False)
    print "Compiling fonts..."
    cFontSrc = compileFont(fSrc)
    cFontDst = compileFont(fDst)
        
    glyphList = fSrc.keys()

    print "Testing all pairs..."
    allSrcPairs = testAllGlyphs(fSrc, cFontSrc, glyphList)
    allDstPairs = testAllGlyphs(fDst, cFontDst, glyphList)
    
    # There should be no hash in allInstancePairs that doesn't already exist in allSourcePairs. Make sure that this is the case.
    # Also, the kern value from the same hash in one font should match the value in the other font (the glyph pair would not match if there was a swap, which is okay)
    print "Comparing results..."
    problem = False
    for dstHash in allDstPairs:
        if not dstHash in allSrcPairs:
            print "\tMissing Pair, the art for", allDstPairs[dstHash][0], "is in the instance but not in the source"
            problem = True
        else:
            sourceKern = allSrcPairs[dstHash][1]
            instanceKern = allDstPairs[dstHash][1]
            if not sourceKern == instanceKern:
                print "\tKern mismatch but with matching art:", allSrcPairs[dstHash], "in source and", allDstPairs[dstHash], "in the instance"
                problem = True
   
    if not problem:
        print "No problems found."     
    print "Done!"
    
        