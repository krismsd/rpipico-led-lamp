import random

from .lambdaColor import LambdaColor
from leds import LedStripControl
from button import Button
from color import Color

class BiColor(LambdaColor):
    def __init__(self, ledStrip: LedStripControl, button: Button, color1, color2) -> None:
        def colorGetter(prev):
            if prev == Color.BLACK:
                return color1 if bool(random.getrandbits(1)) else color2

            if prev == color1:
                return color2
            else:
                return color1

        super().__init__(ledStrip, button, colorGetter, 1000, 500, 1000)
