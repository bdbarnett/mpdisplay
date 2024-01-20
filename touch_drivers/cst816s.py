'''
Adapted from https://github.com/waveshareteam/RP2040-Touch-LCD-1.28/blob/main/python/RP2040-LCD-1.28.py
'''
from machine import Pin
from time import sleep_ms

class Touch_CST816S():
    #Initialize the touch chip
    def __init__(self, bus, address=0x15, mode=1, irq_pin=None, rst_pin=None):
        self._bus = bus
        self._address = int(address) #Set slave address
        self.int = Pin(irq_pin, Pin.IN, Pin.PULL_UP) if irq_pin else None
        self.rst = Pin(rst_pin,Pin.OUT) if rst_pin else None
        self.reset()
        bRet = self.whoami()
        if bRet :
            print("Success:  CST816S detected.")
            rev = self.read_revision()
            print("CST816T Revision = {}".format(rev))
            self.stop_sleep()
        else    :
            print("Error:  CST816S not detected.")
            return None
        self.mode = mode
        self.set_mode(mode)
      
    def _read_byte(self, cmd):
        rec = self._bus.readfrom_mem(self._address, int(cmd), 1)
        return rec[0]
    
    def _read_block(self, reg, length=1):
        rec = self._bus.readfrom_mem(self._address, int(reg), length)
        return rec
    
    def _write_byte(self, cmd, val):
        self._bus.writeto_mem(self._address, int(cmd), bytes([int(val)]))

    def whoami(self):
        if self._read_byte(0xA7) != (0xB5):
            return False
        return True
    
    def read_revision(self):
        return self._read_byte(0xA9)
      
    def stop_sleep(self):
        self._write_byte(0xFE, 0x01)
    
    def reset(self):
        if self.rst:
            self.rst(0)
            sleep_ms(1)
            self.rst(1)
            sleep_ms(50)
    
    def set_mode(self, mode): 
        # mode = 0 gestures mode 
        # mode = 1 point mode 
        # mode = 2 mixed mode 
        if (mode == 1):      
            self._write_byte(0xFA, 0X41)
        elif (mode == 2) :
            self._write_byte(0xFA, 0X71)
        else:
            self._write_byte(0xFA, 0X11)
            self._write_byte(0xEC, 0X01)
     
    def get_point(self):
        if self.int and self.int.value() == 1:
            return None
        xy_point = self._read_block(0x03, 4)
        x = ((xy_point[0] & 0x0f) << 8) + xy_point[1]
        y = ((xy_point[2] & 0x0f) << 8) + xy_point[3]
        return (x, y)

    def get_gestures(self):
        gestures = self._read_byte(0x01)
        return gestures











