from .baseSweepingEffect import BaseSweepingEffect
from leds import LED_POSITIONS, NUM_LEDS
from utils import bound

class ProximaPlane(BaseSweepingEffect):
    def animateFrame(self, position, axis, colors, isForwards):
        color = colors[0]

        for i in range(NUM_LEDS):
            led = LED_POSITIONS[i]
            distance = abs(position - led[axis]) * 3
            scaling = (255 - bound(distance, 0, 255)) / 255 
            finalColor = (int(color[0] * scaling), int(color[1] * scaling), int(color[2] * scaling))

            self.ledStrip.setLed(i, finalColor)

        self.ledStrip.refresh()
