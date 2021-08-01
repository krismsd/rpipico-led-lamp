from .lambdaColor import LambdaColor
from leds import LedStripControl
from button import Button
from utils import getNewRandomColor

class RainbowStars(LambdaColor):
    def __init__(self, ledStrip: LedStripControl, button: Button) -> None:
        def colorGetter(prev):
            return getNewRandomColor(prev)

        super().__init__(ledStrip, button, colorGetter, 4000, 500, 2000)
