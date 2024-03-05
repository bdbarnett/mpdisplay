"""
    lv_config.py - LVGL configuration file
    Save this file as `display_driver.py` to use with LVGL examples
"""

fbuf1 = fbuf2 = None

"""
Uncomment the following 4 lines if you need to allocate buffers as
early as possible to ensure they are in SRAM (if desired).
Note: other imports are out of the suggested order to allow for this.
Substitute width, height, bytes_per_pixel and factor with your values.
"""
# import heap_caps
# buf_size = width*height*bytes_per_pixel // factor
# fbuf1 = heap_caps.malloc(buf_size, heap_caps.CAP_DMA | heap_caps.CAP_INTERNAL)
# fbuf2 = heap_caps.malloc(buf_size, heap_caps.CAP_DMA | heap_caps.CAP_INTERNAL)

import lvgl as lv
import lv_mpdisplay
import board_config

try:
    import lv_utils
    if not lv_utils.event_loop.is_running():
        eventloop = lv_utils.event_loop(asynchronous=False, exception_sink=None)
except ImportError:
    import task_handler
    _task_handler = task_handler.TaskHandler()

# Change color_format to match your display
display = lv_mpdisplay.DisplayDriver(
    board_config.display_drv,
    lv.COLOR_FORMAT.RGB565,
    fbuf1,
    fbuf2,
    factor=10,
    blocking=True,
)

touch = lv_mpdisplay.TouchDriver(
    board_config.touch_read_func,
    rotation=board_config.display_drv.rotation,
    rotation_table=board_config.touch_rotation_table,
)

# Uncomment if your board has an encoder
# encoder = lv_mpdisplay.EncoderDriver(board_config.encoder_read_func, board_config.encoder_button_func)
