""" ILI9486 320x480 on ST Micro STM32 Nucleo-H743ZI2 """

from lcd_bus import I80Bus
from ili9488 import ILI9488 as ILI9486
from machine import SPI, Pin, freq


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
