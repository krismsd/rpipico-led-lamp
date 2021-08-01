from .baseEffect import BaseEffect 
from button import Button
from color import Color
from leds import LedStripControl, NUM_LEDS
from utils import blendChannel, bound

import time
import random

class AnimationState:
    WAITING = 0
    ANIMATING = 1

class LambdaColor(BaseEffect):
    # colorGetter: function
    animationDuration: int
    waitLow: int
    waitHigh: int

    ledState = []

    def __init__(self, ledStrip: LedStripControl, button: Button, colorGetter, animationDuration: int, waitLow: int, waitHigh: int) -> None:
        super().__init__(ledStrip, button)

        self.colorGetter = colorGetter
        self.animationDuration = animationDuration
        self.waitLow = waitLow
        self.waitHigh = waitHigh

    def setup(self):
        for i in range(NUM_LEDS):
            self.ledState.append([
                AnimationState.WAITING,
                time.ticks_ms() +  random.randint(500, 5000),
                self.colorGetter(Color.BLACK),
                Color.BLACK,
            ])

    def loop(self):
        now = time.ticks_ms()

        for i in range(NUM_LEDS):
            led = self.ledState[i]

            if led[0] == AnimationState.WAITING and led[1] < now:
                # Begin animating
                led[0] = AnimationState.ANIMATING
                led[1] = now + self.animationDuration # end animating in 1 second
                led[3] = self.colorGetter(led[2])

            if led[0] == AnimationState.ANIMATING:
                if led[1] < now:
                    # Stop animating
                    led[0] = AnimationState.WAITING
                    led[1] = now + random.randint(self.waitLow, self.waitHigh)
                    led[2] = led[3]
                    led[3] = Color.BLACK

            if led[0] == AnimationState.WAITING:
                self.ledStrip.setLed(i, led[2])
            elif led[0] == AnimationState.ANIMATING:
                transitionPercent = 1 - bound((led[1] - now) / self.animationDuration, 0, 1) 
                color = [blendChannel(led[2][j], led[3][j], transitionPercent) for j in range(3)]
                self.ledStrip.setLed(i, color)

        self.ledStrip.refresh()

        time.sleep_ms(10)
