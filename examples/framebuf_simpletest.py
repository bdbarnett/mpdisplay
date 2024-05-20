"""
Simple test example to demonstrate the use of framebuf.FrameBuffer.
"""

from board_config import display_drv
from framebuf import FrameBuffer, RGB565
from array import array  # for defining a polygon

WIDTH = display_drv.width
HEIGHT = display_drv.height
FONT_WIDTH = 8

# Create a frame buffer
BPP = display_drv.color_depth // 8  # Bytes per pixel
ba = bytearray(WIDTH * HEIGHT * BPP)
fb = FrameBuffer(ba, WIDTH, HEIGHT, RGB565)

# Define colors
color565 = display_drv.color565
WHITE = color565(255, 255, 255)
RED = color565(255, 0, 0)
GREEN = color565(0, 255, 0)
BLUE = color565(0, 0, 255)
CYAN = color565(0, 255, 255)
MAGENTA = color565(255, 0, 255)
YELLOW = color565(255, 255, 0)
BLACK = color565(0, 0, 0)
LTGRAY = color565(192, 192, 192)
GRAY = color565(128, 128, 128)
DKGRAY = color565(64, 64, 64)

# Define objects
triangle = array("h", [0, 0, WIDTH // 2, -HEIGHT // 4, WIDTH - 1, 0])


# Main loop
def loop(
    scroll=False, animate=False, text1="framebuf", text2="simpletest", poly=triangle
):
    y_range = range(HEIGHT - 1, -1, -1) if animate else [HEIGHT - 1]
    for y in y_range:
        fb.fill(BLACK)
        fb.poly(0, y, poly, YELLOW, True)
        fb.fill_rect(WIDTH // 6, HEIGHT // 3, WIDTH * 2 // 3, HEIGHT // 3, LTGRAY)
        fb.line(0, 0, WIDTH - 1, HEIGHT - 1, GREEN)
        fb.rect(0, 0, 15, 15, RED, True)
        fb.rect(WIDTH - 15, HEIGHT - 15, 15, 15, BLUE, True)
        fb.hline(WIDTH // 8, HEIGHT // 2, WIDTH * 3 // 4, MAGENTA)
        fb.vline(WIDTH // 2, HEIGHT // 4, HEIGHT // 2, CYAN)
        fb.pixel(WIDTH // 2, HEIGHT * 1 // 8, WHITE)
        fb.ellipse(
            WIDTH // 2, HEIGHT // 2, WIDTH // 4, HEIGHT // 8, BLACK, True, 0b1111
        )
        fb.text(text1, (WIDTH - FONT_WIDTH * len(text1)) // 2, HEIGHT // 2 - 8, WHITE)
        fb.text(text2, (WIDTH - FONT_WIDTH * len(text2)) // 2, HEIGHT // 2, WHITE)
        display_drv.blit_rect(ba, 0, 0, WIDTH, HEIGHT)

    fb.hline(0, 0, WIDTH, BLACK)
    fb.vline(0, 0, HEIGHT, BLACK)

    scroll_range = range(min(WIDTH, HEIGHT)) if scroll else [0]
    for _ in scroll_range:
        fb.scroll(1, 1)
        display_drv.blit_rect(ba, 0, 0, WIDTH, HEIGHT)


launch = lambda: loop(animate=True)

wipe = lambda: loop(scroll=True)

loop()
