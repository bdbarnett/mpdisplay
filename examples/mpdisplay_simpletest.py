"""
Simple test example to demonstrate the use MPDisplay drawing primitives.
"""

from board_config import display_drv
from array import array  # for defining a polygon

WIDTH = display_drv.width
HEIGHT = display_drv.height
FONT_WIDTH = 8

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
LIGHT_GREY = color565(192, 192, 192)
GREY = color565(128, 128, 128)
DARK_GREY = color565(64, 64, 64)

# Define objects
triangle = array("h", [0, 0, WIDTH // 2, -HEIGHT // 4, WIDTH - 1, 0])


# Main loop
def loop(
    scroll=False, animate=False, text1="MPDisplay", text2="simpletest", poly=triangle
):
    y_range = range(HEIGHT - 1, -1, -1) if animate else [HEIGHT - 1]
    for y in y_range:
        display_drv.fill(BLACK)
        display_drv.poly(0, y, poly, YELLOW, True)
        display_drv.fill_rect(
            WIDTH // 6, HEIGHT // 3, WIDTH * 2 // 3, HEIGHT // 3, LIGHT_GREY
        )
        display_drv.line(0, 0, WIDTH - 1, HEIGHT - 1, GREEN)
        display_drv.rect(0, 0, 15, 15, RED, True)
        display_drv.rect(WIDTH - 15, HEIGHT - 15, 15, 15, BLUE, True)
        display_drv.hline(WIDTH // 8, HEIGHT // 2, WIDTH * 3 // 4, MAGENTA)
        display_drv.vline(WIDTH // 2, HEIGHT // 4, HEIGHT // 2, CYAN)
        display_drv.pixel(WIDTH // 2, HEIGHT * 1 // 8, WHITE)
        display_drv.ellipse(
            WIDTH // 2, HEIGHT // 2, WIDTH // 4, HEIGHT // 8, BLACK, True, 0b1111
        )
        display_drv.text(
            text1, (WIDTH - FONT_WIDTH * len(text1)) // 2, HEIGHT // 2 - 8, WHITE
        )
        display_drv.text(
            text2, (WIDTH - FONT_WIDTH * len(text2)) // 2, HEIGHT // 2, WHITE
        )

    display_drv.hline(0, 0, WIDTH, BLACK)
    display_drv.vline(0, 0, HEIGHT, BLACK)

    scroll_range = range(HEIGHT) if scroll else []
    for _ in scroll_range:
        display_drv.scroll(0, 1)


launch = lambda: loop(animate=True)

wipe = lambda: loop(scroll=True)

loop()
