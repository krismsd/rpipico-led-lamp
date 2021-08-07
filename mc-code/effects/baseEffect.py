import time

from leds import LedStripControl
from button import Button, ButtonCommand

class BaseEffect:
    button: Button
    ledStrip: LedStripControl
    isInfinite: bool
    loopInterval: int

    def __init__(self, ledStrip: LedStripControl, button: Button, isInfinite: bool = True, loopInterval: int = 10) -> None:
        self.ledStrip = ledStrip
        self.button = button
        self.isInfinite = isInfinite
        self.loopInterval = loopInterval
    
    def setup(self):
        pass

    def loop(self):
        pass

    def run(self) -> int:
        self.setup()

        while self.isInfinite:
            buttonResult = self.button.fetchCommand()
            if buttonResult != ButtonCommand.NONE:
                self.ledStrip.clear()
                return buttonResult

            self.loop()
            time.sleep_ms(self.loopInterval)

        return ButtonCommand.NONE
