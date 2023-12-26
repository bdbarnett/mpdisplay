# SPDX-FileCopyrightText: 2023 Brad Barnett
#
# SPDX-License-Identifier: MIT

from machine import Pin, I2C
    
class Chsc6x:
    CHSC6X_I2C_ID = const(0x2e)
    CHSC6X_READ_POINT_LEN = const(5)

    def __init__(self, i2c, addr=CHSC6X_I2C_ID, irq_pin=None):
        self._i2c = i2c
        self._addr = addr
        self._irq = Pin(irq_pin, Pin.IN, Pin.PULL_UP) if irq_pin else None
        self._buffer = bytearray(CHSC6X_READ_POINT_LEN)

    def is_touched(self):
        if self._irq is not None:
            if self._irq.value() == False:
                return True
            return False
        return (self.touch_read() is not None)

    def touch_read(self):
        # Throws an OSError when called repetitively too fast
        try:
            self._i2c.readfrom_into(self._addr, self._buffer)
        except OSError:
            return None
        
        results = [i for i in self._buffer]
        # first byte is non-zero when touched, 3rd byte is x, 5th byte is y
        if results[0]:
            return results[2], results[4]
        return None
     

def main():
    print("Started...")
    i2c = I2C(0, sda=Pin(7), scl=Pin(6))
    touch = Chsc6x(i2c, irq_pin=16)   # with IRQ pin
#     touch = Chsc6x(i2c)               # without IRQ pin 

    while True:
        if touch.is_touched():
            print("Touched: ", touch.touch_read())

if __name__ == "__main__":
    main()