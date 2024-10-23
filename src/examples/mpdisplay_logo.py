from board_config import display_drv
from pygfx.palettes import get_palette
from pygfx import shapes

def main():
    pal = get_palette("material_design")


    CENTER_X = display_drv.width // 2
    CENTER_Y = display_drv.height // 2
    BASE_UNIT = min([display_drv.width, display_drv.height]) // 2

    # Draw the 3 concentric circles
    shapes.circle(display_drv, CENTER_X, CENTER_Y, BASE_UNIT, pal.blue.S900, True)
    shapes.circle(display_drv, CENTER_X, CENTER_Y, int(BASE_UNIT * .9), pal.BLACK, True)
    shapes.circle(display_drv, CENTER_X, CENTER_Y, int(BASE_UNIT * .8), pal.amber.S500, True)

    # Draw the outer rounded rectangle
    LEFT_X = int(CENTER_X - (BASE_UNIT * 1.2) // 2)
    TOP_Y = int(CENTER_Y - (BASE_UNIT * 1.0 ) // 2)
    shapes.round_rect(display_drv, LEFT_X, TOP_Y, int(BASE_UNIT*1.2), int(BASE_UNIT*1.0), BASE_UNIT//7, pal.BLACK, True)

    # Draw the inner rounded rectangle
    LEFT_X = int(CENTER_X - (BASE_UNIT * 1.1) // 2)
    TOP_Y = int(CENTER_Y - (BASE_UNIT * 0.9) // 2)
    shapes.round_rect(display_drv, LEFT_X, TOP_Y, int(BASE_UNIT*1.1), int(BASE_UNIT*0.9), BASE_UNIT//9, pal.amber.S100, True)

    # Draw the 2 small squares
    LEFT_X = CENTER_X - (BASE_UNIT * 3 // 8)
    TOP_Y = CENTER_Y - (BASE_UNIT * 3 // 8)
    SIZE = BASE_UNIT // 4

    shapes.fill_rect(display_drv, LEFT_X, TOP_Y, SIZE, SIZE, pal.BLACK)
    shapes.fill_rect(display_drv, display_drv.width - (LEFT_X + SIZE), display_drv.height - (TOP_Y + SIZE), SIZE, SIZE, pal.BLACK)

    # Draw the 2 small circles
    SIZE = SIZE // 2
    shapes.circle(display_drv, display_drv.width - (LEFT_X + SIZE), TOP_Y + SIZE, SIZE, pal.BLACK, True)
    shapes.circle(display_drv, LEFT_X + SIZE, display_drv.height - (TOP_Y + SIZE), SIZE, pal.BLACK, True)

main()