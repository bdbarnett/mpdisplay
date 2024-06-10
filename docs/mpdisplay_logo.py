from board_config import display_drv
from palettes import get_palette


pal = get_palette("material_design")


CENTER = (display_drv.width//2, display_drv.height//2)

RADIUS = min([display_drv.width, display_drv.height]) // 2

display_drv.circle(*CENTER, RADIUS, pal.blue.S900, True)
display_drv.circle(*CENTER, int(RADIUS * .9), pal.BLACK, True)
display_drv.circle(*CENTER, int(RADIUS * .8), pal.amber.S500, True)


TOP_X = int(CENTER[0] - (RADIUS * 1.2) // 2)
TOP_Y = int(CENTER[1] - (RADIUS * 1.0 ) // 2)
display_drv.round_rect(TOP_X, TOP_Y, int(RADIUS*1.2), int(RADIUS*1.0), RADIUS//7, pal.BLACK, True)

TOP_X = int(CENTER[0] - (RADIUS * 1.1) // 2)
TOP_Y = int(CENTER[1] - (RADIUS * 0.9) // 2)
display_drv.round_rect(TOP_X, TOP_Y, int(RADIUS*1.1), int(RADIUS*0.9), RADIUS//9, pal.amber.S100, True)

TOP_X = CENTER[0] * 5 // 8
TOP_Y = CENTER[1] * 5 // 8
SIZE = CENTER[0] // 4

display_drv.fill_rect(TOP_X, TOP_Y, SIZE, SIZE, pal.BLACK)
display_drv.fill_rect(display_drv.width - (TOP_X+SIZE), display_drv.height - (TOP_Y+SIZE), SIZE, SIZE, pal.BLACK)

SIZE = SIZE // 2
display_drv.circle(display_drv.width - (TOP_X + SIZE),
                   TOP_Y + SIZE,
                   SIZE,
                   pal.BLACK,
                   True)

display_drv.circle(TOP_X + SIZE,
                   display_drv.height - (TOP_Y + SIZE),
                   SIZE,
                   pal.BLACK,
                   True)
