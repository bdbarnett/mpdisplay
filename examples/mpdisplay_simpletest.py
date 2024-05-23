"""
Simple test example to demonstrate the use MPDisplay drawing primitives.
"""

from board_config import display_drv
from array import array  # for defining a polygon

WIDTH = display_drv.width
HEIGHT = display_drv.height
FONT_WIDTH = 8

# Define color palette
pal = display_drv.get_palette()

# Define objects
triangle = array("h", [0, 0, WIDTH // 2, -HEIGHT // 4, WIDTH - 1, 0])


# Main loop
def main(
    scroll=False, animate=False, text1="MPDisplay", text2="simpletest", poly=triangle
):
    y_range = range(HEIGHT - 1, -1, -1) if animate else [HEIGHT - 1]
    for y in y_range:
        display_drv.fill(pal.BLACK)
        display_drv.poly(0, y, poly, pal.YELLOW, True)
        display_drv.fill_rect(
            WIDTH // 6, HEIGHT // 3, WIDTH * 2 // 3, HEIGHT // 3, pal.GREY
        )
        display_drv.line(0, 0, WIDTH - 1, HEIGHT - 1, pal.GREEN)
        display_drv.rect(0, 0, 15, 15, pal.RED, True)
        display_drv.rect(WIDTH - 15, HEIGHT - 15, 15, 15, pal.BLUE, True)
        display_drv.hline(WIDTH // 8, HEIGHT // 2, WIDTH * 3 // 4, pal.MAGENTA)
        display_drv.vline(WIDTH // 2, HEIGHT // 4, HEIGHT // 2, pal.CYAN)
        display_drv.pixel(WIDTH // 2, HEIGHT * 1 // 8, pal.WHITE)
        display_drv.ellipse(
            WIDTH // 2, HEIGHT // 2, WIDTH // 4, HEIGHT // 8, pal.BLACK, True, 0b1111
        )
        display_drv.text(
            text1, (WIDTH - FONT_WIDTH * len(text1)) // 2, HEIGHT // 2 - 8, pal.WHITE
        )
        display_drv.text(
            text2, (WIDTH - FONT_WIDTH * len(text2)) // 2, HEIGHT // 2, pal.WHITE
        )

    display_drv.hline(0, 0, WIDTH, pal.BLACK)
    display_drv.vline(0, 0, HEIGHT, pal.BLACK)

    scroll_range = range(HEIGHT) if scroll else []
    for _ in scroll_range:
        display_drv.scroll(0, 1)


launch = lambda: main(animate=True)

wipe = lambda: main(scroll=True)

main()
