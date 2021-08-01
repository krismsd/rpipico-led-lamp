import time
from machine import Pin

class ButtonCommand:
    NONE = 0
    NEXT = 1
    OFF = 2

class Button:
    __btn: Pin
    __riseStart: int
    __isDown: bool
    __command: int

    def __init__(self, pin: int) -> None:
        self.__btn = Pin(pin, Pin.IN, Pin.PULL_DOWN)
        self.__btn.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=self.buttonCallback)

        self.__riseStart = 0
        self.__isDown = False
        self.__command =  ButtonCommand.NONE

    def buttonRising(self) -> None:
        t = time.ticks_ms()
        if t - self.__riseStart < 400:
            return

        self.__riseStart = t
        self.__isDown = True

    def buttonFalling(self) -> None:
        if not self.__isDown:
            return

        t = time.ticks_ms()
        msSinceRise = t - self.__riseStart
        if msSinceRise < 100:
            return # Assume pin is still bouncing
        elif msSinceRise > 500:
            print("registering button up (long)")
            self.__command = ButtonCommand.OFF
        else:
            print("registering button up (short)")
            self.__command = ButtonCommand.NEXT

        self.__isDown = False

    def buttonCallback(self, p) -> None:
        if p.value():
            self.buttonRising()
        else:
            self.buttonFalling()

    # Get the current command and reset it to none
    def fetchCommand(self) -> int:
        cmd = self.__command
        self.__command = ButtonCommand.NONE
        return cmd
