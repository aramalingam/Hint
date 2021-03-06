#---------------------------------------------------------
# \author Anand Ramalingam                                           
# $Date: 2013/11/07 23:21:00 $
#---------------------------------------------------------
import sys

#---------------------------------------------------------
# class Box
# - Bounding box over the function
#---------------------------------------------------------
class Box(object):

    def __init__(self, x, y):
        assert len(x) == len(y)
        self._x, self._y = x, y

# magic method which is called on invoking print method on a Box instance
    def __str__(self):
# to avoid typing self._x assign to x
# since python uses reference for mutable data
# we are not wasting space
        x, y  = self._x, self._y

        return "x : <'left' = %s, 'right' = %s>, y : <'bottom' = %s, 'top' = %s>" % \
                (x['left'], x['right'], y['bottom'], y['top'])

    def center(self):
        x, y  = self._x, self._y

        npoints = float(len(x))
        result  = {'x' : sum(x.itervalues()) / npoints,
                   'y' : sum(y.itervalues()) / npoints }

        return result

# does the bounding box intersect with f()?
    def intersect(self, f):
        x, y  = self._x, self._y

        return y['bottom'] <= f(x['left'])

# calculate bounds assuming f is a monotonically decreasing function
    def bounds(self, f):
        x, y  = self._x, self._y
        dx    = x['right'] - x['left']

# upper bound
        dy    = self._ubY(f) - y['bottom']
        ub    = dx*dy

# lower bound
        dy    = self._lbY(f) - y['bottom']
        lb    = dx*dy

        result = {'ub' : ub,
                  'lb' : lb }

        return result

# upper bound on y-axis
    def _ubY(self, f):
        x, y  = self._x, self._y
        fxleft = f(x['left'])

        # this assert makes sure that we are have already filtered
        # out boxes which do not intersect with the f()
        assert y['bottom'] <= fxleft 

        # Case 1
        if y['bottom'] <= fxleft <= y['top']:
            ubY = fxleft
        else:
        # Case 2: y['top'] <= f(x['left'])
            ubY = y['top']

        return ubY

# lower bound on y-axis
    def _lbY(self, f):
        x, y  = self._x, self._y
        fxright = f(x['right'])

        # Case 1:
        if fxright <= y['bottom']:
            lbY = y['bottom']
        elif y['bottom'] <= fxright <= y['top']:
        # Case 2: 
            lbY = fxright
        else:
        # Case 3: y['top'] <= f(x['right'])
            lbY = y['top']

        return lbY

# refine a given box by subdividing into four smaller boxes
    def refine(self, f):
        x, y = self._getSubdividedXY()

        # generate four subdivided boxes
        boxes = [Box(i,j) for i in x for j in y]

        # filter out boxes which do not intersect f
        boxes  = [b for b in boxes if b.intersect(f)]

        return boxes

    def _getSubdividedXY(self):
        x, y  = self._x, self._y
        c = self.center()

        xlc = { 'left'  : x['left'],
                'right' : c['x']}

        xcr = { 'left'  : c['x'],
                'right' : x['right']}

        ybc = { 'bottom' :  y['bottom'],
                'top'    :  c['y']}

        yct = { 'bottom' :  c['y'],
                'top'    :  y['top']}

        return [xlc, xcr], [ybc, yct]

#---------------------------------------------------------
# class Grid
# - Grid is a collection of bounding boxes 
# - One can calculate upper and lower bound of bounding box
# - Sum over all the bounding boxes 
#      + this gives bounds on f(x)
#---------------------------------------------------------
class Grid(object):

    def __init__(self, f, x):
        self._f = f
        self._x = x

        # build the initial box 
        # make use of monotonically decreasing attribute of f()
        # f(x(right)) <= f(x(left))
        y = { 'bottom' : f(x['right']),
              'top'    : f(x['left']) }

        b = Box(x, y)
        self._grid = [b]

    def bounds(self):
        boxbounds = [box.bounds(self._f)  for box in self._grid]
        result = {'ub' : sum((bound['ub'] for bound in boxbounds)),
                  'lb' : sum((bound['lb'] for bound in boxbounds))}

        return result

# refine the grid 
    def refine(self):
        finerGrid = []
        for b in self._grid:
            finerGrid.extend(b.refine(self._f))

        self._grid = finerGrid

#---------------------------------------------------------
# hint benchmark
#---------------------------------------------------------
def hint():
    f = lambda x: (1-x)/(1+x)
    # evaluate f over the interval x
    x = { 'left'  : 0,
          'right' : 1}
    g = Grid(f, x)

    # lazy evaluation using generators
    while True:
        yield g.bounds()
        g.refine()

def run(iter):
    print "i, bounds, quality"
    for i, bound in enumerate(hint()):
        # quality is defined as the reciprocal of the difference in the bounds
        # on the running the code, observed an interesting pattern in the
        # quality sequence
        quality = 1.0/(bound['ub'] - bound['lb'])
        print i, bound, quality

        if i == iter:
            break

#------------------------------------------
# main
#------------------------------------------
if __name__ == '__main__':
  argc = len(sys.argv)

  if argc == 2:
    iter = int(sys.argv[1])
  else:
    # default:
    iter = 5

  # finally ... run hint benchmark
  run(iter)
