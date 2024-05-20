"""
Simple test example to demonstrate the use of Shapes.
"""

from board_config import display_drv
from array import array  # for defining a polygon
from primitives import shapes


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
LTGRAY = color565(192, 192, 192)
GRAY = color565(128, 128, 128)
DKGRAY = color565(64, 64, 64)

# Define objects
triangle = array("h", [0, 0, WIDTH // 2, -HEIGHT // 4, WIDTH - 1, 0])


# Main loop
def loop(animate=False, poly=triangle):
    y_range = range(HEIGHT - 1, -1, -1) if animate else [HEIGHT - 1]
    for y in y_range:
        shapes.fill(display_drv, BLACK)
        shapes.poly(display_drv, 0, y, poly, YELLOW, True)
        shapes.fill_rect(
            display_drv, WIDTH // 6, HEIGHT // 3, WIDTH * 2 // 3, HEIGHT // 3, LTGRAY
        )
        shapes.line(display_drv, 0, 0, WIDTH - 1, HEIGHT - 1, GREEN)
        shapes.rect(display_drv, 0, 0, 15, 15, RED, True)
        shapes.rect(display_drv, WIDTH - 15, HEIGHT - 15, 15, 15, BLUE, True)
        shapes.hline(display_drv, WIDTH // 8, HEIGHT // 2, WIDTH * 3 // 4, MAGENTA)
        shapes.vline(display_drv, WIDTH // 2, HEIGHT // 4, HEIGHT // 2, CYAN)
        shapes.pixel(display_drv, WIDTH // 2, HEIGHT * 1 // 8, WHITE)
        shapes.ellipse(
            display_drv,
            WIDTH // 2,
            HEIGHT // 2,
            WIDTH // 4,
            HEIGHT // 8,
            BLACK,
            True,
            0b1111,
        )

    shapes.hline(display_drv, 0, 0, WIDTH, BLACK)
    shapes.vline(display_drv, 0, 0, HEIGHT, BLACK)


launch = lambda: loop(animate=True)

loop()
