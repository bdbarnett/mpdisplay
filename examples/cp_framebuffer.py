from displayio import release_displays
release_displays()

import displayio
import busio
import board
import dotclockframebuffer
from framebufferio import FramebufferDisplay

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

bitmap = displayio.OnDiskBitmap("/display-ruler-720p.bmp")

dcfb = dotclockframebuffer.DotClockFramebuffer(**tft_pins, **tft_timings)
display = FramebufferDisplay(dcfb, auto_refresh=False)

# Create a TileGrid to hold the bitmap
tile_grid = displayio.TileGrid(bitmap, pixel_shader=bitmap.pixel_shader)

# Create a Group to hold the TileGrid
group = displayio.Group()

# Add the TileGrid to the Group
group.append(tile_grid)

# Add the Group to the Display
display.root_group = group

display.auto_refresh = True

# Loop forever so you can enjoy your image
# while True:
#     pass

from framebuf_plus import FrameBuffer, RGB565
from primitives.palettes import get_palette
from array import array

mv = memoryview(dcfb)
WIDTH = dcfb.width
HEIGHT = dcfb.height
FONT_WIDTH = 8

fb = FrameBuffer(mv, WIDTH, HEIGHT, RGB565, dcfb.row_stride//2)


# Define color palette
pal = get_palette(swapped=False)

# Define objects
triangle = array("h", [0, 0, WIDTH // 2, -HEIGHT // 4, WIDTH - 1, 0])


# Main loop
def main(
    scroll=False, animate=False, text1="framebuf", text2="simpletest", poly=triangle
):
    y_range = range(HEIGHT - 1, -1, -1) if animate else [HEIGHT - 1]
    for y in y_range:
        fb.fill(pal.BLACK)
#        fb.poly(0, y, poly, pal.YELLOW, True)
        fb.fill_rect(WIDTH // 6, HEIGHT // 3, WIDTH * 2 // 3, HEIGHT // 3, pal.GREY)
#        fb.line(0, 0, WIDTH - 1, HEIGHT - 1, pal.GREEN)
        fb.rect(0, 0, 15, 15, pal.RED, True)
        fb.rect(WIDTH - 15, HEIGHT - 15, 15, 15, pal.BLUE, True)
        fb.hline(WIDTH // 8, HEIGHT // 2, WIDTH * 3 // 4, pal.MAGENTA)
        fb.vline(WIDTH // 2, HEIGHT // 4, HEIGHT // 2, pal.CYAN)
#        fb.pixel(WIDTH // 2, HEIGHT * 1 // 8, pal.WHITE)
        fb.ellipse(
            WIDTH // 2, HEIGHT // 2, WIDTH // 4, HEIGHT // 8, pal.BLACK, True, 0b1111
        )
        fb.text(text1, (WIDTH - FONT_WIDTH * len(text1)) // 2, HEIGHT // 2 - 8, pal.WHITE)
        fb.text(text2, (WIDTH - FONT_WIDTH * len(text2)) // 2, HEIGHT // 2, pal.WHITE)
#         display_drv.blit_rect(ba, 0, 0, WIDTH, HEIGHT)

    fb.hline(0, 0, WIDTH, pal.BLACK)
    fb.vline(0, 0, HEIGHT, pal.BLACK)

    scroll_range = range(min(WIDTH, HEIGHT)) if scroll else [0]
#     for _ in scroll_range:
#         fb.scroll(1, 1)
#         display_drv.blit_rect(ba, 0, 0, WIDTH, HEIGHT)


launch = lambda: main(animate=True)

wipe = lambda: main(scroll=True)

main()

