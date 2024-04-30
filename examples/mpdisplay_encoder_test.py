"""
A simple test of an encoder in MPDisplay.
"""
from board_config import display_drv
from mpdisplay import Events

color_byte = 1
w = display_drv.width
h = display_drv.height
thickness = 10
position = 0

def draw_line():
    global color_byte

    color = color_byte << 8 | color_byte
    display_drv.fill_rect(0, (h-thickness)//2, w, thickness, color)
    color_byte = color_byte << 1 & 0xFF
    if color_byte == 0:
        color_byte = 1

draw_line()

while True:
    if not (e := display_drv.poll_event()):
        continue
    if e.type == Events.MOUSEWHEEL:
        direction = 1 if e.y > 0 else -1
        delta = e.y * e.y * direction  # Quadratic acceleration
        position += delta
        display_drv.vscsad(position % display_drv.height)
    elif e.type == Events.MOUSEBUTTONDOWN and e.button == 2:
        draw_line()
