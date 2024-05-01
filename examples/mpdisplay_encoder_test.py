"""
A simple test of an encoder in MPDisplay.
"""
from board_config import display_drv
from mpdisplay import Events

color_byte = 1
box_color = -1
w = display_drv.width
h = display_drv.height
thickness = 10
position = 0

def draw_line():
    global color_byte

    color = color_byte << 8 | color_byte
    display_drv.fill_rect(0, h-thickness, w, thickness, color)

def draw_box():
    display_drv.fill_rect(w//4, h//4, w//2, h//2, box_color)

draw_line()
draw_box()

while True:
    if not (e := display_drv.poll_event()):
        continue
    if e.type == Events.MOUSEWHEEL:
        if e.y != 0:
            direction = 1 if e.y > 0 else -1
            delta = e.y * e.y * direction  # Quadratic acceleration
            position += delta
            display_drv.vscsad(position % display_drv.height)
        if e.x != 0:
            direction = 1 if e.x > 0 else -1
            delta = e.x * e.x * direction
            box_color += delta
            draw_box()
    elif e.type == Events.MOUSEBUTTONDOWN:
        if e.button == 2:
            color_byte = color_byte << 1 & 0xFF
            if color_byte == 0:
                color_byte = 1
            draw_line()
        elif e.button == 3:
            box_color = -1
            draw_box()
