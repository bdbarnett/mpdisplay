""" LILYGO T-QT Pro GC9107 128x128 display """
# Usage:
# `from <this file> import display_drv``
# or just use this file as your main.py and add your code.

import mpdisplay
from gc9107 import init_sequence, rotations
from backlight import Backlight
from machine import Pin

# To use baudrates above 26.6MHz you must modify the micropython source code to increase the SPI baudrate
# limit by adding SPI_DEVICE_NO_DUMMY to the .flag member of the spi_device_interface_config_t struct in the
# machine_hw_spi.c file.  Not doing so will cause the ESP32 to crash if you use a baudrate that is too high.
# https://github.com/micropython/micropython/blob/fce8d9fd55409ab1027beee5671bc653fb5beb97/ports/esp32/machine_hw_spi.c#L241

bus = mpdisplay.Spi_bus(
    1,
    mosi=2,
    sck=3,
    dc=6,
    cs=5,
    pclk=60_000_000,
)

display_drv = mpdisplay.Display(
    bus,
    width=128,
    height=128,
    bpp=16,
    reset=1,
    rotation=0,
    bgr=True,
    invert_color=True,
    init_sequence=init_sequence,
    rotations=rotations,
)

backlight=Backlight(Pin(10, Pin.OUT),on_high=False)
