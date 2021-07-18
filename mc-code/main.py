# Example using PIO to drive a set of WS2812 LEDs.

import array, time
from machine import Pin
import rp2
import math

# Configure the number of WS2812 LEDs.
PIN_NUM = 28
brightness = 0.75

LED_POSITIONS = ((-109, -53, -30), (-5, -53, -30), (-65, 37, 74), (-109, -67, 74), (99, 37, 74), (55, -67, 0), (-109, 37, -74), (-35, -7, -74), (69, -7, -74), (-109, 23, -30), (-35, -17, -30), (69, -17, -30), (109, 23, -30), (35, 67, 0))
RANGEX = (-109, 109)
RANGEY = (-67, 67)
RANGEZ = (-74, 74)

NUM_LEDS = len(LED_POSITIONS)

@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT, autopull=True, pull_thresh=24)
def ws2812():
    T1 = 2
    T2 = 5
    T3 = 3
    wrap_target()
    label("bitloop")
    out(x, 1)               .side(0)    [T3 - 1]
    jmp(not_x, "do_zero")   .side(1)    [T1 - 1]
    jmp("bitloop")          .side(1)    [T2 - 1]
    label("do_zero")
    nop()                   .side(0)    [T2 - 1]
    wrap()


# Create the StateMachine with the ws2812 program, outputting on pin
sm = rp2.StateMachine(0, ws2812, freq=8_000_000, sideset_base=Pin(PIN_NUM))

# Start the StateMachine, it will wait for data on its FIFO.
sm.active(1)

# Display a pattern on the LEDs via an array of LED RGB values.
ar = array.array("I", [0 for _ in range(NUM_LEDS)])

##########################################################################
def pixels_show():
    dimmer_ar = array.array("I", [0 for _ in range(NUM_LEDS)])
    for i,c in enumerate(ar):
        r = int(((c >> 8) & 0xFF) * brightness)
        g = int(((c >> 16) & 0xFF) * brightness)
        b = int((c & 0xFF) * brightness)
        dimmer_ar[i] = (g<<16) + (r<<8) + b
    sm.put(dimmer_ar, 8)
    #time.sleep_ms(10)

def pixels_set(i, color):
    ar[i] = (color[1]<<16) + (color[0]<<8) + color[2]

def pixels_fill(color):
    for i in range(len(ar)):
        pixels_set(i, color)

def color_chase(color, wait):
    for i in range(NUM_LEDS):
        pixels_set(i, color)
        time.sleep(wait)
        pixels_show()
    time.sleep(0.2)

def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        return (0, 0, 0)
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    if pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    pos -= 170
    return (pos * 3, 0, 255 - pos * 3)


def rainbow_cycle(wait):
    for j in range(255):
        for i in range(NUM_LEDS):
            rc_index = (i * 256 // NUM_LEDS) + j
            pixels_set(i, wheel(rc_index & 255))
        pixels_show()
        time.sleep(wait)

BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)
WHITE = (255, 255, 255)
COLORS = (RED, YELLOW, GREEN, CYAN, BLUE, PURPLE, WHITE) # BLACK

# print("fills")
# for color in COLORS:
#     pixels_fill(color)
#     pixels_show()
#     time.sleep(0.2)

# print("chases")
# for color in COLORS:
#     color_chase(color, 0.01)

# while True:
#     print("rainbow")
#     rainbow_cycle(0)



# while True:
#     for i in range(180):
#         pixels_fill((0, i, 0))
#         pixels_show()
#         time.sleep(0)
#     for i in range(180, 0, -1):
#         pixels_fill((0, i, 0))
#         pixels_show()
#         time.sleep(0)


import random

BTN_NONE = 0
BTN_NEXT = 1

riseStart = 0
buttonCmd = BTN_NONE
def buttonCallback(p):
    global riseStart, buttonCmd

    t = time.ticks_ms()
    if t - riseStart < 400:
        return

    riseStart = t

    print("registering button pressed")
    buttonCmd = BTN_NEXT

button = Pin(27, Pin.IN, Pin.PULL_DOWN)
button.irq(trigger=Pin.IRQ_RISING, handler=buttonCallback)


def blendChannel(a, b, t):
    if t == 0:
        return a
    elif t == 1:
        return b
    else:
        return int(math.sqrt((1 - t) * a**2 + t * b**2))
      

def bound(value, smallest, largest):
    return min(max(value, smallest), largest)


def wipePlane(ord, posIdx, color, bgColor, isForwards):
    for i in range(NUM_LEDS):
        led = LED_POSITIONS[i]
        distance = (led[posIdx] - ord)
        
        distance *= 3

        foregroundAlpha = bound(distance, 0, 175) / 175
        if not isForwards:
            foregroundAlpha = 1 - foregroundAlpha

        finalColor = (
            blendChannel(color[0], bgColor[0], foregroundAlpha),
            blendChannel(color[1], bgColor[1], foregroundAlpha),
            blendChannel(color[2], bgColor[2], foregroundAlpha),
        )

        pixels_set(i, finalColor)

    pixels_show()

def proximaPlane(ord, posIdx, color):
    for i in range(NUM_LEDS):
        led = LED_POSITIONS[i]
        distance = abs(ord - led[posIdx]) * 3
        scaling = (255 - min(max(distance, 0), 255)) / 255 
        # scaled = min(max(255 - int(distance * 2), 0), 255)
        finalColor = (int(color[0] * scaling), int(color[1] * scaling), int(color[2] * scaling))
        pixels_set(i, finalColor)

    pixels_show()

def clearLeds():
    for i in range(NUM_LEDS):
        pixels_set(i, BLACK)
    pixels_show()


def checkButtonNext():
    global buttonCmd

    if buttonCmd == BTN_NEXT:
        buttonCmd = BTN_NONE
        clearLeds()
        return True
    else:
        return False

def getNewRandomColor(previous):
    color = None
    while color == None or previous == color:
        color = COLORS[random.randint(0, len(COLORS) - 1)]
    return color

def loopWipePlane():
    ANIMATION_DURATION = 4000

    xyzRanges = (RANGEX, RANGEY, RANGEZ)
    color = BLACK

    print("BEGIN: wipe plane")
    while True:
        for xyzIdx in (0, 1): # x, y axis
            r = xyzRanges[xyzIdx]
            padding = 100
            low = r[0] - padding
            high = r[1] + padding

            distance = high - low

            for isForwards in (True, False):
                bgColor = color # Use previous color as "background" for this wipe
                color = getNewRandomColor(color)

                start = time.ticks_ms()
                while True:
                    if checkButtonNext():
                        return
                    
                    now = time.ticks_ms()
                    animationProgress = (now - start) / ANIMATION_DURATION

                    if animationProgress > 1:
                        break

                    if not isForwards:
                        animationProgress = 1 - animationProgress

                    wipePlane(int(distance * animationProgress) + low, xyzIdx, color, bgColor, isForwards)
                    time.sleep_ms(10)
           
            

def loopRainbowStars():
    # each led starts of a random color
    # for each led after a random interval if has a change to start transitioning to another random color
    print("BEGIN: loop rainbow stars")

    WAITING = 0
    ANIMATING = 1

    ANIMATE_DURATION = 4000


    ledState = [] # List of [waiting/animating, animate start/animation progress, current color, new color]
    for i in range(NUM_LEDS):
        ledState.append([
            WAITING,
            time.ticks_ms() +  random.randint(500, 5000),
            COLORS[random.randint(0, len(COLORS) - 1)],
            BLACK,
        ])

    while True:
        if checkButtonNext():
            return
        
        now = time.ticks_ms()

        for i in range(NUM_LEDS):
            led = ledState[i]

            if led[0] == WAITING and led[1] < now:
                # Begin animating
                led[0] = ANIMATING
                led[1] = now + ANIMATE_DURATION # end animating in 1 second
                led[3] = getNewRandomColor(led[2])

            if led[0] == ANIMATING:
                if led[1] < now:
                    # Stop animating
                    led[0] = WAITING
                    led[1] = now + random.randint(500, 5000)
                    led[2] = led[3]
                    led[3] = BLACK

            if led[0] == WAITING:
                pixels_set(i, led[2])
            elif led[0] == ANIMATING:
                transitionPercent = 1 - bound((led[1] - now) / ANIMATE_DURATION, 0, 1) 
                color = [blendChannel(led[2][j], led[3][j], transitionPercent) for j in range(3)]
                pixels_set(i, color)

        pixels_show()

        time.sleep_ms(10)

def loopShowSolid(color):
    print("BEGIN: show solid")

    for i in range(NUM_LEDS):
        pixels_set(i, color)
    pixels_show()

    while True:
        if checkButtonNext():
            return
        time.sleep_ms(200)


def waitForButton():
    print("BEGIN: wait for button")
    while True:
        if checkButtonNext():
            return
        time.sleep_ms(200)

while True:
    loopRainbowStars()
    loopWipePlane()
    for i in range(len(COLORS)):
        loopShowSolid(COLORS[i])

    waitForButton()
