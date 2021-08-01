import math
import random

from color import Color

def blendChannel(a, b, t):
    if t == 0:
        return a
    elif t == 1:
        return b
    else:
        return int(math.sqrt((1 - t) * a**2 + t * b**2))
      

def bound(value, smallest, largest):
    return min(max(value, smallest), largest)

def getNewRandomColor(previous):
    color = None
    while color == None or previous == color:
        color = Color.ALL[random.randint(0, len(Color.ALL) - 1)]
    return color
