
"""
    This is a script for Drawbot (http://drawbot.com)
    It draws a graph of the factors of a 2-axis, 4 master designspace.
    

"""
from mutatorMath.objects.mutator import buildMutator
from mutatorMath.objects.location import Location

import random as rann
import os, time, math
import itertools

class MathDot(object):
    def __init__(self, pt=(0,0), s=0.5, alpha=1, name=None):
        self.pt = pt
        self.size = s
        self.alpha = alpha
        self.name = name
    
    def draw(self):
        save()
        s = self.size * .5
        fill(1,0,0, self.alpha)
        oval(self.pt[0]-.5*s, self.pt[1]-0.5*s, s, s)
        fill(1,0.5,0)
        stroke(None)
        fontSize(9 * 0.1)
        text("%s\n%3.2f"%(self.name, self.size), (self.pt[0], self.pt[1]-3))
        restore()
        
    def __repr__(self):
        return "<MathDot %3.1f, %3.1f %s>"%(self.pt[0],self.pt[1], self.name)
        
    def copy(self):
        return self.__class__(self.pt, self.size, self.alpha, self.name)
        
    def __add__(self, other):
        new = self.copy()
        new.pt = new.pt[0]+other.pt[0], new.pt[1]+other.pt[1]
        new.size += other.size
        new.alpha += other.alpha
        return new
    
    def __sub__(self, other):
        new = self.copy()
        new.pt = new.pt[0]-other.pt[0], new.pt[1]-other.pt[1]
        new.size -= other.size
        new.alpha -= other.alpha
        return new

    def __div__(self, factor):
        if not isinstance(factor, tuple):
            factor = (factor, factor)
        new = self.copy()
        new.pt = self.pt[0]/factor[0], self.pt[1]/factor[1]
        new.size = self.size/factor[0]
        new.alpha = self.alpha/factor[0]
        return new
        
    def __mul__(self, factor):
        if not isinstance(factor, tuple):
            factor = (factor, factor)
        new = self.copy()
        new.pt = self.pt[0]*factor[0], self.pt[1]*factor[1]
        new.size *= factor[0]      
        new.alpha = self.alpha*factor[0]
        return new
        
    __rmul__ = __mul__    


items = [
   (Location(pop=0, snap=0), MathDot((0,0), name="neutral")),
   (Location(pop=0, snap=1), MathDot((0, 100), name="on-axis-one-A")),
   (Location(pop=1, snap=0), MathDot((100, 0), name="on-axis-two-A")),
   (Location(pop=1, snap=1), MathDot((100, 100), name="off-axis-A")),
]

bias, mb = buildMutator(items)

grid = {}
for loc, (master, xx) in mb.items():
    for axis, value in loc:
        if not axis in grid:
            grid[axis] = []
        if not (axis,value) in grid[axis]:
            grid[axis].append((axis,value))
nodes = list(itertools.product(*grid.values()))
nodes.sort()

corners = {}
for n in nodes:
    l = Location()
    l.fromTuple(n)
    for factor, obj, name in mb.getFactors(l, allFactors=True):
        if not obj.name in corners:
            corners[obj.name] = []
        corners[obj.name].append((factor, l))

def dot((x,y), s=10):
    save()
    fill(1,0,0 ,.5)
    oval(x-.5*s, y-.5*s, s, s)
    restore()

def nameToStroke(name, alpha=1):
    # simple conversion of a name to some sort of unique-ish color.
    rann.seed(name)
    fill(None)
    stroke(rann.random(), 0, rann.random(), alpha)

def nameToFill(name, alpha=1):
    # simple conversion of a name to some sort of unique-ish color.
    rann.seed(name)
    stroke(None)
    fill(rann.random(), 0, rann.random(), alpha)

# make the drawings
for name in corners:
    newPage(500,500)
    designSpaceScale = 250
    save()
    margin = 102
    translate(margin, margin)
    projectionAngle = math.radians(20)
    strokeWidth(10)
    stroke(.5)
    fill(None)
    a = b = 1    # scale these to the number of masters on an axis
    line((0,0), (0,designSpaceScale*a))
    line((0,0), (designSpaceScale*b, 0))

    polyPts = []
    for factor, loc in corners[name]:
        save()
        dy = math.cos(projectionAngle) * factor * designSpaceScale *.5
        dx = math.sin(projectionAngle) * factor * designSpaceScale *.5
        pos1 = (loc['pop']*designSpaceScale+dx, loc['snap']*designSpaceScale+dy)
        pos2 = (loc['pop']*designSpaceScale, loc['snap']*designSpaceScale)
        polyPts.append(pos1)

        nameToStroke(name, 1)
        strokeWidth(10)
        line(pos1, pos2)
        dot(pos1)
        dot(pos2)
        w, h = textSize(name)
        pos3 = pos1[0] - w -10, pos1[1]
        strokeWidth(20)
        nameToStroke(name, 0.4)
        line(pos1, pos3)
        fill(1)
        stroke(None)
        text(name, pos3)
        restore()
    
    # draw the plane
    # note: these polygons are hardwired to the number of masters.
    # While you can easily add more masters to see what the factors do,
    # these surfaces won't do the right thing.
    if len(polyPts)==4:
        stroke(None)
        nameToFill(name, 0.25)
        polygon(polyPts[0], polyPts[1], polyPts[3])
        if "off" in name:
            nameToFill(name, 0.15)
        polygon(polyPts[0], polyPts[2], polyPts[3])
    restore()

    path = os.path.join(os.getcwd(), "mutatorMath_pyramids_wedges_%s.png"%(name))
    saveImage(path)
