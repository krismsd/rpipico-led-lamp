import time

from .lambdaColor import BaseEffect
from leds import AXIS_RANGES, LedStripControl
from button import Button
from color import Color
from utils import getNewRandomColor

class BaseSweepingEffect(BaseEffect):
    ANIMATION_DURATION = 4000

    # animationGenerator: Generator
    # animation: tuple | None
    animationStart: int

    def __init__(self, ledStrip: LedStripControl, button: Button) -> None:
        super().__init__(ledStrip, button)

    def setup(self):
        self.animationGenerator = wipingAnimationGenerator()
        self.animation = None
        self.animationStart = 0

    def loop(self):
        now = time.ticks_ms()
        animationProgress = (now - self.animationStart) / self.ANIMATION_DURATION

        if animationProgress > 1 or self.animation is None:
            self.animation = next(self.animationGenerator)
            self.animationStart = time.ticks_ms()
            animationProgress = 0

        (axis, isForwards, colors) = self.animation

        if not isForwards:
            animationProgress = 1 - animationProgress

        (min, max) = AXIS_RANGES[axis]
        padding = 100
        low = min - padding
        high = max + padding

        position = int((high - low) * animationProgress) + low

        self.animateFrame(position, axis, colors, isForwards)

    def animateFrame(self, position, axis, colors, isForwards):
        pass

def wipingAnimationGenerator():
    # An infinite generator that will loop over each axis (x,y,z) in both directions (forward, reverse)
    # For each axis/direction a new color will be chosen with the color from the previous wipe being 
    # used as the background for the next  
    color = Color.BLACK

    while True:
        for axis in range(len(AXIS_RANGES)):
            for isForwards in (True, False):
                bgColor = color # Use previous color as "background" for next wipe
                color = getNewRandomColor(color)

                yield (axis, isForwards, (color, bgColor))

