from .baseSweepingEffect import BaseSweepingEffect
from leds import LED_POSITIONS, NUM_LEDS
from utils import bound, blendChannel

class WipePlane(BaseSweepingEffect):
    def animateFrame(self, position, axis, colors, isForwards):
        (color, bgColor) = colors

        for i in range(NUM_LEDS):
            led = LED_POSITIONS[i]
            distance = (led[axis] - position)

            # How far the transition should extend (should be less than the padding around the axis to avoid 
            # the animation looking like it didn't complete before moving on)
            scaling = 50
            
            foregroundAlpha = bound(distance, 0, scaling) / scaling
            if not isForwards:
                foregroundAlpha = 1 - foregroundAlpha

            finalColor = (
                blendChannel(color[0], bgColor[0], foregroundAlpha),
                blendChannel(color[1], bgColor[1], foregroundAlpha),
                blendChannel(color[2], bgColor[2], foregroundAlpha),
            )

            self.ledStrip.setLed(i, finalColor)

        self.ledStrip.refresh()
