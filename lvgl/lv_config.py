"""
    lv_config.py - LVGL configuration file
    Save this file as `display_driver.py` to use with LVGL examples
"""

import board_config

###################### Create framebuffers before loading LVGL
try:
    from lcd_bus import MEMORY_32BIT, MEMORY_8BIT, MEMORY_DMA, MEMORY_SPIRAM, MEMORY_INTERNAL, MEMORY_DEFAULT

    caps = MEMORY_DMA | MEMORY_INTERNAL  ### Change to your requirements.  Bitwise OR of buffer memory capabilities
    alloc_buffer = board_config.display_bus.allocate_framebuffer
except:
    caps = None
    alloc_buffer = lambda buffersize, caps: memoryview(bytearray(buffer_size))

factor = 10  ### Must be 1 if using an RGBBus
double_buf = True  ### Must be False if using an RGBBus

buffer_size = board_config.display_drv.width \
              * board_config.display_drv.height \
              * (board_config.display_drv.color_depth // 8) \
              // factor

fbuf1 = alloc_buffer(buffer_size, caps)
fbuf2 = alloc_buffer(buffer_size, caps) if double_buf else None


###################### Load LVGL and continue setting up
import lv_mpdisplay
from lvgl import COLOR_FORMAT

### Change color_format to match your display
display = lv_mpdisplay.DisplayDriver(
    board_config.display_drv,
    fbuf1,
    fbuf2,
    COLOR_FORMAT.RGB565,
    blocking=True,
)

touch = lv_mpdisplay.TouchDriver(
    board_config.touch_read_func,
    rotation=board_config.display_drv.rotation,
    rotation_table=board_config.touch_rotation_table,
)

### Uncomment if your board has an encoder
# encoder = lv_mpdisplay.EncoderDriver(board_config.encoder_read_func, board_config.encoder_button_func)
