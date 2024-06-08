"""
    lv_config.py - LVGL configuration file
    Save this file as `display_driver.py` to use with LVGL examples
"""

from board_config import display_drv
import lvgl as lv
import gc


###################### Create the buffers

lv.init()
gc.collect()
color_format = lv.COLOR_FORMAT.RGB565
draw_buf1 = lv.draw_buf_create(display_drv.width, display_drv.height // 10, color_format, 0)
draw_buf2 = lv.draw_buf_create(display_drv.width, display_drv.height // 10, color_format, 0)

###################### Continue setting up

import lv_mpdisplay

display = lv_mpdisplay.DisplayDriver(
    display_drv,
    draw_buf1,
    draw_buf2,
    color_format,
    blocking=True,
)
