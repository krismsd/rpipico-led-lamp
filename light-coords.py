### Script for calculating end positions of LED tree given sequence of joined parts and known lengths of parts

LEFT = "left"
RIGHT = "right"
UP = "up"
DOWN = "down"
IN = "in"
OUT = "out"
STRAIGHT = "straight"
LONGSTRAIGHT = "longstraight"

class v:
    turnHalf = 13
    straight = 40
    longstraight = 80
    connect = 4

    facingMap = { # Index of dimension (x, y, z) and direction in dimension
        RIGHT: (0, 1),
        LEFT: (0, -1),
        UP: (1, 1),
        DOWN: (1, -1),
        IN: (2, 1),
        OUT: (2, -1),
    }

    def __init__(self, x, y, z, facing):
        self.x = x
        self.y = y
        self.z = z
        self.facing = facing

    def __add__(self, dir):
        plot = [self.x, self.y, self.z]

        currentFacingData = self.facingMap[self.facing]

        # Add connector length
        plot[currentFacingData[0]] += self.connect * currentFacingData[1]


        if dir == STRAIGHT or dir == LONGSTRAIGHT:
            # Add in direction of current facing
            plot[currentFacingData[0]] += (self.straight if dir == STRAIGHT else self.longstraight) * currentFacingData[1]

            dir = self.facing
        else:
            # We're turning so add half turn in current facing, then another half turn in new facing
            newFacingData = self.facingMap[dir]

            plot[currentFacingData[0]] += self.turnHalf * currentFacingData[1]
            plot[newFacingData[0]] += self.turnHalf * newFacingData[1]

        return v(
            *plot,
            dir,
        )

    def __repr__(self):
        return "(%s, %s, %s, %s)" % (self.x, self.y, self.z, self.facing)

    def endpoint(self):
        return (self.x, self.y, self.z)


t0 = v(-5, -111, 0, UP) # Root coordinate adjusted so all LEDs are centered around 0,0,0

tA = t0 + LONGSTRAIGHT
tAA = tA + LEFT + STRAIGHT + OUT + DOWN

tB = tA + UP
tBA = tB + IN + STRAIGHT
tBAA = tBA + LEFT 
tBAB = tBA + RIGHT

tC = tB + UP
tCA = tC + OUT + STRAIGHT

tD = tC + UP
tDA = tD + OUT
tDAA = tDA + LEFT

tE = tD + UP
tEA = tE + RIGHT + LONGSTRAIGHT + DOWN

leds = (
    tAA + LEFT + DOWN,
    tAA + RIGHT + STRAIGHT + DOWN,
    
    tBAA + UP + LEFT + DOWN,
    tBAA + DOWN + STRAIGHT + LEFT + STRAIGHT + DOWN,
    tBAB + UP + RIGHT + STRAIGHT + DOWN,
    tBAB + DOWN + STRAIGHT + RIGHT + OUT + STRAIGHT + DOWN,

    tCA + LEFT + LEFT + STRAIGHT + DOWN,
    tCA + LEFT + DOWN + STRAIGHT,
    tCA + RIGHT + STRAIGHT + DOWN + STRAIGHT,

    tDAA + LEFT + STRAIGHT + DOWN + STRAIGHT,
    tDAA + DOWN + LONGSTRAIGHT,
    tDA + RIGHT + STRAIGHT + DOWN + LONGSTRAIGHT,

    tEA + OUT + DOWN + STRAIGHT,
    tEA + LEFT + STRAIGHT + DOWN,
)

print(list(map(lambda led: led.endpoint(), leds)))

lsX = list(map(lambda led: led.x, leds))
lsY = list(map(lambda led: led.y, leds))
lsZ = list(map(lambda led: led.z, leds))

print ("x range: " + str((min(lsX), max(lsX))))
print ("y range: " + str((min(lsY), max(lsY))))
print ("z range: " + str((min(lsZ), max(lsZ))))
