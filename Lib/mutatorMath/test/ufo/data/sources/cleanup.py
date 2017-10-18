for f in AllFonts():
    for g in f:
        l = g.getLayer("background")
        l.clear()
    f.save()