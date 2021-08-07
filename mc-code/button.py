import time
from machine import Pin, Timer

class ButtonCommand:
    NONE = 0
    NEXT = 1
    OFF = 2

class Button:
    __btn: Pin
    __riseStart: int
    __isDown: bool
    __command: int
    __checkTimer: Timer
    __holdTimer: Timer

    def __init__(self, pin: int) -> None:
        self.__btn = Pin(pin, Pin.IN, Pin.PULL_DOWN)
        self.__btn.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=self.buttonCallback)

        self.__riseStart = 0
        self.__isDown = False
        self.__command =  ButtonCommand.NONE

        self.__checkTimer = Timer()
        self.__holdTimer = Timer()

    def buttonRising(self) -> None:
        t = time.ticks_ms()
        if t - self.__riseStart < 400:
            return

        self.__riseStart = t
        self.__isDown = True

        self.__checkTimer.deinit()
        self.__checkTimer.init(period=100, mode=Timer.ONE_SHOT, callback=self.checkTimerCallback)

        self.__holdTimer.deinit()
        self.__holdTimer.init(period=500, mode=Timer.ONE_SHOT, callback=self.holdTimerCallback)

    def buttonFalling(self) -> None:
        if not self.__isDown:
            return

        t = time.ticks_ms()
        msSinceRise = t - self.__riseStart
        if msSinceRise < 40:
            return # Assume pin is still bouncing
        # elif msSinceRise > 500:
        #     print("registering button up (long)")
        #     self.__command = ButtonCommand.OFF
        else:
            print("button up, registering next command")
            self.__command = ButtonCommand.NEXT

        self.__holdTimer.deinit()
        self.__isDown = False

    def buttonCallback(self, p) -> None:
        if p.value():
            self.buttonRising()
        else:
            self.buttonFalling()

    def checkTimerCallback(self, timer) -> None:
        if not self.__btn.value():
            print("check timer check failed, ignoring button down")
            self.__holdTimer.deinit()
            self.__isDown = False

    def holdTimerCallback(self, timer) -> None:
        print("timer elapsed, registering off command")
        self.__command = ButtonCommand.OFF
        self.__isDown = False

    # Get the current command and reset it to none
    def fetchCommand(self) -> int:
        cmd = self.__command
        self.__command = ButtonCommand.NONE
        return cmd
