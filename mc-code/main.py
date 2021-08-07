import time

from leds import LedStripControl
from button import ButtonCommand, Button
from color import Color
import effects

LEDSTRIP_DATA_PIN = 28
BUTTON_PIN = 27

ledStrip = LedStripControl(LEDSTRIP_DATA_PIN)
button = Button(BUTTON_PIN)


effectFns: list = [
    effects.ProximaPlane(ledStrip, button),
    effects.WipePlane(ledStrip, button),
    effects.BiColor(ledStrip, button, Color.PURPLE, Color.CYAN),
    effects.BiColor(ledStrip, button, Color.GREEN, Color.PURPLE),
    effects.BiColor(ledStrip, button, Color.WHITE, Color.GREEN),
    effects.RainbowStars(ledStrip, button),
]

def loopEffects():
    while True:
        for effectFn in effectFns:
            buttonCmd = effectFn.run()
            if buttonCmd == ButtonCommand.OFF:
                return

def waitForButton():
    print("BEGIN: wait for button")
    while True:
        if button.fetchCommand() == ButtonCommand.NEXT:
            return
        time.sleep_ms(200)

while True:
    loopEffects()
    waitForButton()
