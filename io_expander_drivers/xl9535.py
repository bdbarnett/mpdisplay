"""
License:  GPL-3.0
see https://github.com/Xinyuan-LilyGO/lilygo-micropython/tree/master/target/esp32s3/boards/LILYGO_T-RGB/modules
"""

from machine import I2C, Pin
from micropython import const

__XL9535_IIC_ADDRESS = const(0X20)

__XL9535_INPUT_PORT_0_REG     = const(0X00)
__XL9535_INPUT_PORT_1_REG     = const(0X01)
__XL9535_OUTPUT_PORT_0_REG    = const(0X02)
__XL9535_OUTPUT_PORT_1_REG    = const(0X03)
__XL9535_INVERSION_PORT_0_REG = const(0X04)
__XL9535_INVERSION_PORT_1_REG = const(0X05)
__XL9535_CONFIG_PORT_0_REG    = const(0X06)
__XL9535_CONFIG_PORT_1_REG    = const(0X07)


class XL9535():
    OUT = Pin.OUT
    IN = Pin.IN
    def __init__(self, bus: I2C, a0: bool = False, a1: bool = False, a2: bool = False):
        self.__bus = bus
        self.__address = __XL9535_IIC_ADDRESS | \
                         (int(a2) << 3) | \
                         (int(a1) << 2) | \
                         (int(a0) << 1)
        self.__buf = bytearray(1)
        try:
            self.__bus.scan().index(self.__address)
        except:
            raise Exception("XL9535 not found")

    def pinMode(self, pin, mode):
        if pin > 7:
            self.__bus.readfrom_mem_into(self.__address,
                                         __XL9535_CONFIG_PORT_1_REG,
                                         self.__buf)
            if mode == self.OUT:
                self.__buf[0] = self.__buf[0] & (~(1 << (pin - 10)))
            else:
                self.__buf[0] = self.__buf[0] | (1 << (pin - 10))
            self.__bus.writeto_mem(self.__address,
                                   __XL9535_CONFIG_PORT_1_REG,
                                   self.__buf)
        else:
            self.__bus.readfrom_mem_into(self.__address,
                                         __XL9535_CONFIG_PORT_0_REG,
                                         self.__buf)
            if mode == self.OUT:
                self.__buf[0] = self.__buf[0] & (~(1 << pin))
            else:
                self.__buf[0] = self.__buf[0] | (1 << pin)
            self.__bus.writeto_mem(self.__address,
                                   __XL9535_CONFIG_PORT_0_REG,
                                   self.__buf)

    def pinMode8(self, port, pin, mode):
        self.__buf[0] = pin if mode != self.OUT else ~pin
        if port:
            self.__bus.writeto_mem(self.__address,
                                   __XL9535_CONFIG_PORT_1_REG,
                                   self.__buf)
        else:
            self.__bus.writeto_mem(self.__address,
                                   __XL9535_CONFIG_PORT_0_REG,
                                   self.__buf)

    def digitalWrite(self, pin, val):
        val = 1 if val else 0
        if pin > 7:
            self.__bus.readfrom_mem_into(self.__address,
                                         __XL9535_CONFIG_PORT_1_REG,
                                         self.__buf)
            self.__buf[0] = self.__buf[0] & (~(1 << (pin - 10)))
            self.__buf[0] = self.__buf[0] | val << (pin - 10)
            self.__bus.writeto_mem(self.__address,
                                   __XL9535_CONFIG_PORT_1_REG,
                                   bytes(self.__buf))
        else:
            self.__bus.readfrom_mem_into(self.__address,
                                         __XL9535_OUTPUT_PORT_0_REG,
                                         self.__buf)
            self.__buf[0] = self.__buf[0] & (~(1 << pin))
            self.__buf[0] = self.__buf[0] | val << pin
            self.__bus.writeto_mem(self.__address,
                                   __XL9535_OUTPUT_PORT_0_REG,
                                   self.__buf)
            
# The remainder of this file was added by Brad Barnett
    def digitalRead(self, pin):
        if pin > 7:
            self.__bus.readfrom_mem_into(self.__address,
                                         __XL9535_INPUT_PORT_1_REG,
                                         self.__buf)
            return (self.__buf[0] >> (pin - 10)) & 1
        self.__bus.readfrom_mem_into(self.__address,
                                     __XL9535_INPUT_PORT_0_REG,
                                     self.__buf)
        return (self.__buf[0] >> pin) & 1
    
    def Pin(self, pin, mode=-1, *, value=None):
        """
        Create a Pin object for the XL9535 I2C IO expander
        
        :param pin: pin number
        :param mode: Pin.IN or Pin.OUT
        :param value: initial value of the pin
        """
        return Pin((self, pin), mode, value=value)


class Pin():
    """
    Pin class for the XL9535 I2C IO expander
    
    :param id: tuple of (io_expander, pin)
    :param mode: Pin.IN or Pin.OUT
    :param value: initial value of the pin
    """
    OUT = Pin.OUT
    IN = Pin.IN
    def __init__(self, id, mode=-1, *, value=None):
        self.__io_expander, self.__pin = id
        if mode != -1:
            self.init(mode, value=value)

    def init(self, mode, *, value=None):
        """
        Initialize the pin
        
        :param mode: Pin.IN or Pin.OUT
        :param value: initial value of the pin
        """
        self.__io_expander.pinMode(self.__pin, mode)
        if value is not None:
            self.value(value)

    def value(self, val=None):
        """
        Get or set the value of the pin

        :param val: value to set the pin to
        """
        if val is None:
            return self.__io_expander.digitalRead(self.__pin)
        self.__io_expander.digitalWrite(self.__pin, val)
    
    def __call__(self, val=None):
        """
        Get or set the value of the pin

        :param val: value to set the pin to
        """
        self.value(val)

    def on(self):
        """
        Set the pin to 1
        """
        self.value(1)

    def off(self):
        """
        Set the pin to 0
        """
        self.value(0)
