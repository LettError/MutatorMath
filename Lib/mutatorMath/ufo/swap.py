
"""

    Swap the contents of two glyphs.
        - contours
        - components
        - width
        - group membership
        - kerning

    Remap components so that glyphs that reference either of the swapped glyphs maintain appearance
    Keep the unicode value of the original glyph

"""
def swapGlyphname(font, oldName, newName, swapNameExtension = "_______________swap"):
    if not oldName in font or not newName in font:
        return None
    swapName = oldName + swapNameExtension
    # park the old glyph 
    if not swapName in font:
        font.newGlyph(swapName)
    # swap the outlines
    font[swapName].clear()
    p = font[swapName].getPointPen()
    font[oldName].drawPoints(p)
    font[swapName].width = font[oldName].width
    
    font[oldName].clear()
    p = font[oldName].getPointPen()
    font[newName].drawPoints(p)
    font[oldName].width = font[newName].width
    
    font[newName].clear()
    p = font[newName].getPointPen()
    font[swapName].drawPoints(p)
    font[newName].width = font[swapName].width
    
    # remap the components
    for g in font:
        for c in g.components:
           if c.baseGlyph == oldName:
               c.baseGlyph = swapName
           continue
    for g in font:
        for c in g.components:
           if c.baseGlyph == newName:
               c.baseGlyph = oldName
           continue
    for g in font:
        for c in g.components:
           if c.baseGlyph == swapName:
               c.baseGlyph = newName
   
    # change the names in groups
    # the shapes will swap, that will invalidate the kerning
    # so the names need to swap in the kerning as well.
    newKerning = {}
    for first, second in font.kerning.keys():
        value = font.kerning[(first,second)]
        if first == oldName:
            first = newName
        elif first == newName:
            first = oldName
        if second == oldName:
            second = newName
        elif second == newName:
            second = oldName
        newKerning[(first, second)] = value
    font.kerning.clear()
    font.kerning.update(newKerning)
            
    for groupName, members in font.groups.items():
        newMembers = []
        for name in members:
            if name == oldName:
                newMembers.append(newName)
            elif name == newName:
                newMembers.append(oldName)
            else:
                newMembers.append(name)
        font.groups[groupName] = newMembers
    
    remove = []
    for g in font:
        if g.name.find(swapNameExtension)!=-1:
            remove.append(g.name)
    for r in remove:
        del font[r]


if __name__ == "__main__":
    import os
    from defcon.objects.font import Font
    root = os.getcwd()
    srcPath = os.path.join(root, "../", "test", "ufo", "data", "sources", "swap", "Swap.ufo")    #"../../test/ufo/data/sources/swap/RulesTestFont.ufo"
    dstPath = os.path.join(root, "../", "test", "ufo", "data", "instances", "S", "SwapTestOutput.ufo")    #"../../test/ufo/data/sources/swap/RulesTestFont.ufo"
    
    f = Font(srcPath)
    swapGlyphname(f, "a", "a.alt")
    swapGlyphname(f, "adieresis", "adieresis.alt")
    f.info.styleName = "Swapped"
    f.save(dstPath)
    
    # test the results in newly opened fonts
    old = Font(srcPath)
    new = Font(dstPath)
    assert new.kerning.get(("a", "a")) == old.kerning.get(("a.alt","a.alt"))
    assert new.kerning.get(("a.alt", "a.alt")) == old.kerning.get(("a","a"))
    assert old['a'].unicode == new['a'].unicode

