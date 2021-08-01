import array
from machine import Pin
import rp2

LED_POSITIONS = ((-109, -53, -30), (-5, -53, -30), (-65, 37, 74), (-109, -67, 74), (99, 37, 74), (55, -67, 0), (-109, 37, -74), (-35, -7, -74), (69, -7, -74), (-109, 23, -30), (-35, -17, -30), (69, -17, -30), (109, 23, -30), (35, 67, 0))
NUM_LEDS = len(LED_POSITIONS)

RANGE_X = (-109, 109)
RANGE_Y = (-67, 67)
RANGE_Z = (-74, 74)
AXIS_RANGES = (RANGE_X, RANGE_Y, RANGE_Z)

class LedStripControl:
    sm: rp2.StateMachine
    ar = array.array("I", [0 for _ in range(NUM_LEDS)])
    globalBrightness: int = 1

    def __init__(self, dataPinNum) -> None:
        @rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT, autopull=True, pull_thresh=24)
        def ws2812():
            T1 = 2
            T2 = 5
            T3 = 3
            wrap_target()
            label("bitloop")
            out(x, 1)               .side(0)    [T3 - 1]
            jmp(not_x, "do_zero")   .side(1)    [T1 - 1]
            jmp("bitloop")          .side(1)    [T2 - 1]
            label("do_zero")
            nop()                   .side(0)    [T2 - 1]
            wrap()

        # Create the StateMachine with the ws2812 program, outputting on pin
        self.sm = rp2.StateMachine(0, ws2812, freq=8_000_000, sideset_base=Pin(dataPinNum))
        self.sm.active(1)

    def refresh(self):
        dimmer_ar = array.array("I", [0 for _ in range(NUM_LEDS)])
        for i,c in enumerate(self.ar):
            r = int(((c >> 8) & 0xFF) * self.globalBrightness)
            g = int(((c >> 16) & 0xFF) * self.globalBrightness)
            b = int((c & 0xFF) * self.globalBrightness)
            dimmer_ar[i] = (g<<16) + (r<<8) + b
        self.sm.put(dimmer_ar, 8)
        #time.sleep_ms(10)

    def setLed(self, i, color):
        self.ar[i] = (color[1]<<16) + (color[0]<<8) + color[2]

    def clear(self):
        for i in range(NUM_LEDS):
            self.setLed(i, (0, 0, 0))
        self.refresh()
