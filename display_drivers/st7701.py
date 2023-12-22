"""
see https://github.com/Xinyuan-LilyGO/lilygo-micropython/tree/master/target/esp32s3/boards/LILYGO_T-RGB/modules
"""

from busdisplay import BusDisplay
from time import sleep_ms


_INIT_SEQUENCE = [
    (0xFF, b'\x77\x01\x00\x00\x10', 0),
    (0xC0, b'\x3b\x00', 0),
    (0xC1, b'\x0b\x02', 0),
    (0xC2, b'\x07\x02', 0),
    (0xCC, b'\x10', 0),
    (0xCD, b'\x08', 0), # 用565时屏蔽    666打开
    (0xb0, b'\x00\x11\x16\x0e\x11\x06\x05\x09\x08\x21\x06\x13\x10\x29\x31\x18', 0),
    (0xb1, b'\x00\x11\x16\x0e\x11\x07\x05\x09\x09\x21\x05\x13\x11\x2a\x31\x18', 0),
    (0xFF, b'\x77\x01\x00\x00\x11', 0),
    (0xb0, b'\x6d', 0),
    (0xb1, b'\x37', 0),
    (0xb2, b'\x81', 0),
    (0xb3, b'\x80', 0),
    (0xb5, b'\x43', 0),
    (0xb7, b'\x85', 0),
    (0xb8, b'\x20', 0),
    (0xc1, b'\x78', 0),
    (0xc2, b'\x78', 0),
    (0xc3, b'\x8c', 0),
    (0xd0, b'\x88', 0),
    (0xe0, b'\x00\x00\x02', 0),
    (0xe1, b'\x03\xa0\x00\x00\x04\xa0\x00\x00\x00\x20\x20', 0),
    (0xe2, b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', 0),
    (0xe3, b'\x00\x00\x11\x00', 0),
    (0xe4, b'\x22\x00', 0),
    (0xe5, b'\x05\xec\xa0\xa0\x07\xee\xa0\xa0\x00\x00\x00\x00\x00\x00\x00\x00', 0),
    (0xe6, b'\x00\x00\x11\x00', 0),
    (0xe7, b'\x22\x00', 0),
    (0xe8, b'\x06\xed\xa0\xa0\x08\xef\xa0\xa0\x00\x00\x00\x00\x00\x00\x00\x00', 0),
    (0xeb, b'\x00\x00\x40\x40\x00\x00\x00', 0),
    (0xed, b'\xff\xff\xff\xba\x0a\xbf\x45\xff\xff\x54\xfb\xa0\xab\xff\xff\xff', 0),
    (0xef, b'\x10\x0d\x04\x08\x3f\x1f', 0),
    (0xFF, b'\x77\x01\x00\x00\x13', 0),
    (0xef, b'\x08', 0),
    (0xFF, b'\x77\x01\x00\x00\x00', 0),
    (0x36, b'\x08', 0),
    (0x3a, b'\x66', 0),
    (0x11, b'\x00', 100),
    # (0xFF,  b'\x77\x01\x00\x00\x12', 0),
    # (0xd1,  b'\x81', 0),
    # (0xd2,  b'\x06', 0),
    (0x29, b'\x00', 100)
]


class IOPins():
    def __init__(self, write, *, tp_res, pwr_en, lcd_cs, lcd_sda, lcd_clk, lcd_rst, sd_cs):
        self.write = write
        self.tp_res = tp_res
        self.pwr_en = pwr_en
        self.lcd_cs = lcd_cs
        self.lcd_sda = lcd_sda
        self.lcd_clk = lcd_clk
        self.lcd_rst = lcd_rst
        self.sd_cs = sd_cs


class ST7701(BusDisplay):
    """
    ST7701 display driver

    :param io_expander: the io expander to configure the display
    """

    def _init_(self, io_pins, *args, **kwargs):

        self.io_pins = io_pins

        self.io_pins.write(self.io_pins.pwr_en, 1)
        self.io_pins.write(self.io_pins.lcd_cs, 1)
        self.io_pins.write(self.io_pins.lcd_sda, 1)
        self.io_pins.write(self.io_pins.lcd_clk, 1)

        # Reset the display
        self.io_pins.write(self.io_pins.lcd_rst, 1)
        sleep_ms(200)
        self.io_pins.write(self.io_pins.lcd_rst, 0)
        sleep_ms(200)
        self.io_pins.write(self.io_pins.lcd_rst, 1)
        sleep_ms(200)

        super()._init_(*args, **kwargs)

    def init(self):
        for line in _INIT_SEQUENCE:
            self.set_params(line[0], line[1])
            if line[2] != 0:
                sleep_ms(line[2])
        # print("Register setup complete")
        super.init()

    def set_params(self, cmd, params=None):
        self._tx_cmd(cmd)
        if params:
            self._tx_data(params)

    def _tx_cmd(self, cmd):
        self.io_pins.write(self.io_pins.lcd_cs, 0)
        self.io_pins.write(self.io_pins.lcd_sda, 0)
        self.io_pins.write(self.io_pins.lcd_clk, 0)
        self.io_pins.write(self.io_pins.lcd_clk, 1)
        self._tx_byte(cmd)
        self.io_pins.write(self.io_pins.lcd_cs, 1)

    def _tx_data(self, data):
        for i in range(len(data)):
            self.io_pins.write(self.io_pins.lcd_cs, 0)
            self.io_pins.write(self.io_pins.lcd_sda, 1)
            self.io_pins.write(self.io_pins.lcd_clk, 0)
            self.io_pins.write(self.io_pins.lcd_clk, 1)
            self._tx_byte(data[i])
            self.io_pins.write(self.io_pins.lcd_cs, 1)

    def _tx_byte(self, bits):
        for _ in range(8):
            if (bits & 0x80):
                self.io_pins.write(self.io_pins.lcd_sda, 1)
            else:
                self.io_pins.write(self.io_pins.lcd_sda, 0)
            bits <<= 1
            self.io_pins.write(self.io_pins.lcd_clk, 0)
            self.io_pins.write(self.io_pins.lcd_clk, 1)
