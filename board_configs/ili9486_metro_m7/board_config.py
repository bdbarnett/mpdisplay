""" ILI9486 320x480 on Adafruit Metro M7 """

from lcd_bus import I80Bus
from ili9488 import ILI9488 as ILI9486
from machine import SPI, Pin, freq  # See the note about reset below


# The WT32-SC01 Plus has the reset pins of the display IC and the touch IC both
# tied to pin 4.  Controlling this pin with the display driver can lead to an
# unresponsive touchscreen.  This case is uncommon.  If they aren't tied 
# together on your board, define reset in ST7796 instead, like:
#    ST7796(reset=4)
reset=Pin(4, Pin.OUT, value=1)

display_bus = I80Bus(
    dc=Pin.board.A2,
    wr=Pin.board.A1,
    cs=Pin.board.A3,
    data0=Pin.board.D8,
    data1=Pin.board.D9,
    data2=Pin.board.D2,
    data3=Pin.board.D3,
    data4=Pin.board.D4,
    data5=Pin.board.D5,
    data6=Pin.board.D6,
    data7=Pin.board.D7,
    freq=10_000_000,
)

display_drv = ILI9486(
    display_bus,
    width=320,
    height=480,
    colstart=0,
    rowstart=0,
    rotation=0,
    mirrored=False,
    color_depth=16,
    bgr=True,
    reverse_bytes_in_word=True,
    invert=True,
    brightness=1.0,
    backlight_pin=None,
    backlight_on_high=True,
#    reset_pin=Pin.board.A4,
    reset_high=True,
    power_pin=None,
    power_on_high=True,
    )

touch_read_func = lambda: None
touch_rotation_table = None
