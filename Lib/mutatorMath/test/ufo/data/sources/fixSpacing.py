
for f in AllFonts():
    if 'Wide' in f.info.styleName:
        wk = 'wide'
    else:
        wk = 'cond'
    if 'Bold' in f.info.styleName:
        bk = 'bold'
    else:
        bk = 'light'

    print 'current', wk, bk
    groups = {
        "L_straight":    ['B', 'D', 'E', 'F', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'P', 'R', 'U', 'Z', "quotesinglbase", "quotedblbase", "period", "comma", "colon", "semicolon", "quotedblright", "quotedblleft"],
        "R_straight":    [ 'E', 'F', 'G', 'H', 'I', 'J', 'M', 'N', 'U', 'Z', "quotesinglbase", "quotedblbase", "period", "comma", "colon", "semicolon", "quotedblright", "quotedblleft"],
        "L_angled":    ['A', 'V', 'W', 'X', 'Y'],
        "R_angled":    ['A', 'K', 'V', 'W', 'X', 'Y'],
        "L_short":    ['T', ],
        "R_short":    ['L', 'T', 'P', 'R', 'B', ],
        "L_round":    ['C','G', 'O', 'Q', 'S'],
        "R_round":    ['C', 'D', 'O', 'Q', 'S'],
    }


    margins = {
        'bold': {
            'straight': dict(cond=30, wide=60),
            'angled':  dict(cond=10, wide=20),
            'round': dict(cond=20, wide=40),
            'short': dict(cond=20, wide=20),
            },
        'light': {
            'straight': dict(cond=60, wide=120),
            'angled':  dict(cond=20, wide=40),
            'round': dict(cond=50, wide=80),
            'short': dict(cond=30, wide=40),
            },
    }
    
    for n in f.keys():
        #print n
        for k, v in groups.items():
            if n in v:
                parts = k.split("_")
                left = None
                right = None
                if parts[0] == "L":
                    left = margins[bk].get(parts[1])[wk]
                    #print "links", n, k, left
                elif parts[0] == "R":
                    right = margins[bk].get(parts[1])[wk]
                    #print "rechts", n, k, right
                if n in f:
                    if left:
                        f[n].leftMargin = left
                    if right:
                        f[n].rightMargin = right
                    
