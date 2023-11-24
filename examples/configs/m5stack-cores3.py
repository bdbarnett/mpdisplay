"""M5STACK CORES3 with ili9342c 320x240 display"""
# Usage:
# `from <this file> import display_drv``
# or just use this file as your main.py and add your code.

import mpdisplay
from ili9342c import init_sequence, rotations
from backlight import Backlight
from machine import Pin

# To use baudrates above 26.6MHz you must modify the micropython source code to increase the SPI baudrate
# limit by adding SPI_DEVICE_NO_DUMMY to the .flag member of the spi_device_interface_config_t struct in the
# machine_hw_spi.c file.  Not doing so will cause the ESP32 to crash if you use a baudrate that is too high.
# https://github.com/micropython/micropython/blob/fce8d9fd55409ab1027beee5671bc653fb5beb97/ports/esp32/machine_hw_spi.c#L241

bus = mpdisplay.Spi_bus(
    1,
    mosi=37,
    sck=36,
    dc=35,
    cs=3,
    pclk=60_000_000,
    swap_color_bytes=True,
)

display_drv = mpdisplay.Display(
    bus,
    width=240,
    height=320,
    bpp=16,
    reset=-1,
    rotation=2,
    bgr=True,
    invert_color=True,
    init_sequence=init_sequence,
    rotations=rotations,
    backlight=None,
)
