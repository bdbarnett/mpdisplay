""" DIY ESP32 psram with and ILI9341 2.8" display and XPT2046 touch controller"""

from lcd_bus import SPIBus
from ili9341 import ILI9341
from machine import Pin, SPI
from xpt2046 import Touch
from eventsys.devices import Devices

display_bus = SPIBus(
    dc=5,
    host=1,
    mosi=13,
    miso=12,
    sclk=14,
    cs=15,
    freq=40_000_000,
    wp=-1,
    hd=-1,
    quad_spi=False,
    tx_only=True,
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
    rotation=270,
    mirrored=False,
    color_depth=16,
    bgr=True,
    reverse_bytes_in_word=True,
    invert=False,
    brightness=1.0,
    backlight_pin=None,
    backlight_on_high=True,
    reset_pin=4,
    reset_high=False,
    power_pin=22,
    power_on_high=True,
)

spi = SPI(2, baudrate=1000000, sck=Pin(18), mosi=Pin(23), miso=Pin(19))
touch_drv = Touch(
    spi=spi,
    cs=Pin(25),
    int_pin=Pin(21),
)

#Display rotation 270 degrees, invert Y axis 0b100
touch_drv.calibrate(
    xmin=107,
    xmax=2000,
    ymin=200,
    ymax=1940,
    width=display_drv.height,
    height=display_drv.width,
    orientation=3,
)

touch_read_func=touch_drv.get_touch,
touch_rotation_table = (0b000, 0b000, 0b000, 0b100)

touch_dev = broker.create_device(
    type=Devices.TOUCH,
    read=touch_read_func,
    data=touch_rotation_table,
)
