"""
see https://github.com/Xinyuan-LilyGO/lilygo-micropython/tree/master/target/esp32s3/boards/LILYGO_T-RGB/modules
"""

from busdisplay import BusDisplay
from time import sleep_ms


_INIT_SEQUENCE = [
    (0x11, b'\x00', 120),               # Exit sleep mode
    (0x13, b'\x00', 0),                 # Turn on the display
    (0xb6, b'\x0a\x82', 0),             # Set display function control
    (0x31, b'\x55', 10),                # Set pixel format to 16 bits per pixel (RGB565)
    (0xb2, b'\x0c\x0c\x00\x33\x33', 0), # Set porch control
    (0xb7, b'\x35', 0),                 # Set gate control
    (0xbb, b'\x28', 0),                 # Set VCOMS setting
    (0xc0, b'\x0c', 0),                 # Set power control 1
    (0xc2, b'\x01\xff', 0),             # Set power control 2
    (0xc3, b'\x10', 0),                 # Set power control 3
    (0xc4, b'\x20', 0),                 # Set power control 4
    (0xc6, b'\x0f', 0),                 # Set VCOM control 1
    (0xd0, b'\xa4\xa1', 0),             # Set power control A
                                            # Set gamma curve positive polarity
    (0xe0, b'\xd0\x00\x02\x07\x0a\x28\x32\x44\x42\x06\x0e\x12\x14\x17', 0),
                                            # Set gamma curve negative polarity
    (0xe1, b'\xd0\x00\x02\x07\x0a\x28\x31\x54\x47\x0e\x1c\x17\x1b\x1e', 0),
    (0x21, b'\x00', 0),                 # Enable display inversion
    (0x29, b'\x00', 120),               # Turn on the display
]


class ST7789(BusDisplay):
    """
    ST7789 display driver
    """

    def _init_(self, *args, **kwargs):
        super()._init_(*args, **kwargs)

    def init(self):
#         self.rotation_table = _ROTATION_TABLE
        for line in _INIT_SEQUENCE:
            self.set_params(line[0], line[1])
            if line[2] != 0:
                sleep_ms(line[2])
        # print("Register setup complete")
        super().init()
