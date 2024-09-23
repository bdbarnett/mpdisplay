from board_config import display_drv, broker
from gfx import Draw
from palettes import get_palette
from time import sleep
from random import getrandbits


def main():
    line_height = 16
    display_drv.set_vscroll(16, 16)

    pal = get_palette()
    draw = Draw(display_drv)

    if display_drv.tfa > 0:
        # draw top fixed area
        draw.fill_rect(0, 0, display_drv.width, display_drv.tfa, pal.RED)
        if display_drv.tfa > 15:
            draw.text14("0 TFA", 1, 1, pal.WHITE)
            draw.round_rect(display_drv.width - 44, 1, 40, 12, 4, pal.GREEN, True)
            draw.text("Up", display_drv.width - 32, 4, pal.WHITE)
    if display_drv.bfa > 0:
        # draw bottom fixed area
        draw.fill_rect(0, display_drv.height - display_drv.bfa, display_drv.width, display_drv.bfa, pal.BLUE)
        if display_drv.bfa > 15:
            draw.text14(f"{display_drv.height - display_drv.bfa} BFA", 1, display_drv.height - display_drv.bfa + 1, pal.WHITE)
            draw.round_rect(display_drv.width - 44, display_drv.height - display_drv.bfa + 1, 40, 12, 4, pal.GREEN, True)
            draw.text("Down", display_drv.width - 40, display_drv.height - display_drv.bfa + 5, pal.WHITE)

    for i, y in enumerate(range(display_drv.tfa, display_drv.vsa + display_drv.tfa, line_height)):
        # Draw alternating bars on the scrollable area
        fg, bg = pal.WHITE, pal.BLACK
        if i % 2:
            fg, bg = bg, fg
        draw.fill_rect(0, y, display_drv.width, 16, bg)
        txt = f"abs: {y}, rel: {y - display_drv.tfa}"
        draw.text14(txt, 1, y + 1, fg)
        draw.rect(display_drv.width - 20, y + 2, 12, 12, fg)

    while True:
        # Check for mouse events
        if evt := broker.poll():
            if evt.type == broker.Events.MOUSEBUTTONDOWN:
                x, y = display_drv.translate_point(evt.pos)
                if y < display_drv.tfa:
                    display_drv.vscroll -= 16
                elif y > display_drv.height - display_drv.bfa:
                    display_drv.vscroll += 16
                else:
                    y_pos = (y // line_height) * line_height
                    display_drv.fill_rect(display_drv.width - 20, y_pos + 2, 12, 12, getrandbits(display_drv.color_depth))

main()
