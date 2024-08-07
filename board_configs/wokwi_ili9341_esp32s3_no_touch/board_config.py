""" Wokwi ESP32S3 and ILI9341 Display """

from lcd_bus import SPIBus
from ili9341 import ILI9341


display_bus = SPIBus(
    dc=16,
    host=1,
    mosi=35,
    miso=37,
    sclk=36,
    cs=5,
    freq=60_000_000,
    wp=-1,
    hd=-1,
    quad_spi=False,
    tx_only=False,  # This line changed for Wokwi
    cmd_bits=8,
    param_bits=8,
    dc_low_on_data=False,
    sio_mode=False,
    lsb_first=False,
    cs_high_active=False,
    spi_mode=0,
)

display_drv = ILI9341(
    display_bus,
    width=240,
    height=320,
    colstart=0,
    rowstart=0,
    rotation=0,
    mirrored=False,
    color_depth=16,
    bgr=True,
    reverse_bytes_in_word=True,
    invert=False,
    brightness=1.0,
    backlight_pin=None,
    backlight_on_high=True,
    reset_pin=None,
    reset_high=True,
    power_pin=None,
    power_on_high=True,
)
