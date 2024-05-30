from displayio import release_displays
release_displays()

import displayio
import busio
import board
import dotclockframebuffer
from framebufferio import FramebufferDisplay
from mpdisplay import FBDisplay

tft_pins = dict(board.TFT_PINS)

tft_timings = {
    "frequency": 16000000,
    "width": 720,
    "height": 720,
    "hsync_pulse_width": 2,
    "hsync_front_porch": 46,
    "hsync_back_porch": 44,
    "vsync_pulse_width": 2,
    "vsync_front_porch": 16,
    "vsync_back_porch": 18,
    "hsync_idle_low": False,
    "vsync_idle_low": False,
    "de_idle_high": False,
    "pclk_active_high": False,
    "pclk_idle_high": False,
}

init_sequence_tl040hds20 = bytes()

board.I2C().deinit()
i2c = busio.I2C(board.SCL, board.SDA)
tft_io_expander = dict(board.TFT_IO_EXPANDER)
#tft_io_expander['i2c_address'] = 0x38 # uncomment for rev B
dotclockframebuffer.ioexpander_send_init_sequence(i2c, init_sequence_tl040hds20, **tft_io_expander)
i2c.deinit()

dcfb = dotclockframebuffer.DotClockFramebuffer(**tft_pins, **tft_timings)


display = FramebufferDisplay(dcfb, auto_refresh=False)
# bitmap = displayio.OnDiskBitmap("/display-ruler-720p.bmp")
# tile_grid = displayio.TileGrid(bitmap, pixel_shader=bitmap.pixel_shader)# Create a TileGrid to hold the bitmap
# group = displayio.Group()# Create a Group to hold the TileGrid
# group.append(tile_grid)# Add the TileGrid to the Group
# display.root_group = group# Add the Group to the Display
display.auto_refresh = True


display_drv = FBDisplay(dcfb)

