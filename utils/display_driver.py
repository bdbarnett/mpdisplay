from display_config import display_drv, backlight
from i2c_config import touch_drv
from lvmp_devices import Devices
import mpdisplay

devices = Devices(
    display_drv = display_drv,
    bgr = True,
    factor = 6,
    blit_func = display_drv.blit,
    alloc_buf_func = display_drv.allocate_buffer,
    register_ready_cb_func = display_drv.register_cb,
    touch_read_func = touch_drv.get_positions,
    touch_rotation = 5,
    )

devices.backlight = backlight
