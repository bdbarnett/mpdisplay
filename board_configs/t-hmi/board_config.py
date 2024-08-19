""" T-HMI 240x320 ST7789V display """

from lcd_bus import I80Bus
from st7789 import ST7789
from machine import SPI, Pin  # See the note about reset below
from xpt2046 import Touch
from eventsys.devices import Devices


display_bus = I80Bus(
    dc=7,
    wr=8,
    cs=6,
    data0=48,
    data1=47,
    data2=39,
    data3=40,
    data4=41,
    data5=42,
    data6=45,
    data7=46,
    freq=20000000,
    dc_idle_level=0,
    dc_cmd_level=0,
    dc_dummy_level=0,
    dc_data_level=1,
    cmd_bits=8,
    param_bits=8,
    cs_active_high=False,
    reverse_color_bits=False,
    pclk_active_neg=False,
    pclk_idle_low=False,
)

display_drv = ST7789(
    display_bus,
    width=320,
    height=240,
    colstart=0,
    rowstart=0,
    rotation=0,
    mirrored=False,
    color_depth=16,
    bgr=False,
    reverse_bytes_in_word=False,
    invert=True,
    brightness=1.0,
    backlight_pin=38,
    backlight_on_high=True,
    reset_pin=None,
    reset_high=True,
    power_pin=None,
    power_on_high=True,
)

spi = SPI(1, baudrate=1000000)
touch_drv = Touch(
    spi=spi,
    cs=Pin(2),
    int_pin=Pin(9),
)

touch_drv.calibrate(
    xmin=150,
    xmax=1830,
    ymin=150,
    ymax=1830,
    width=display_drv.width,
    height=display_drv.height,
    orientation=1,
)

touch_read_func = touch_drv.get_touch
touch_rotation_table=None

touch_dev = broker.create_device(
    type=Devices.TOUCH,
    read=touch_read_func,
    data=touch_rotation_table,
)
