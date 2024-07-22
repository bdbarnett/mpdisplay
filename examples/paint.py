"""
A simple paint application demonstrating the use of MPDisplay.
"""

from board_config import display_drv
from graphics.palettes import get_palette
from mpdisplay import Events


display_drv.rotation = 90

pal = get_palette()
colors = [pal.WHITE, pal.RED, pal.GREEN, pal.BLUE, pal.CYAN, pal.MAGENTA, pal.YELLOW, pal.BLACK]

on_x_axis = display_drv.width < display_drv.height
block_size = min(display_drv.width, display_drv.height) // len(colors)
selected_pad = block_size // 10
brush_size = 5
selected = 0


def draw_block(index, color):
    x, y = (index * block_size, 0) if on_x_axis else (0, index * block_size)
    if index == selected:
        display_drv.fill_rect(x, y, block_size, block_size, pal.GREY)
        display_drv.fill_rect(
            x + selected_pad,
            y + selected_pad,
            block_size - 2 * selected_pad,
            block_size - 2 * selected_pad,
            color,
        )
    else:
        display_drv.fill_rect(x, y, block_size, block_size, color)


def paint(x, y, color):
    display_drv.fill_rect(
        x - brush_size // 2, y - brush_size // 2, brush_size, brush_size, color
    )


for i, color in enumerate(colors):
    draw_block(i, color)


while True:
    if not (e := display_drv.broker.poll()):
        continue
    if e.type == Events.MOUSEBUTTONDOWN:
        x, y = e.pos
        last_selected = selected
        if on_x_axis and y < block_size or not on_x_axis and x < block_size:
            if on_x_axis:
                selected = x // block_size
            else:
                selected = y // block_size
            if selected != last_selected:
                draw_block(last_selected, colors[last_selected])
                draw_block(selected, colors[selected])
            if e.button == 3:
                if on_x_axis:
                    display_drv.fill_rect(
                        0,
                        block_size,
                        display_drv.width,
                        display_drv.height - block_size,
                        colors[selected],
                    )
                else:
                    display_drv.fill_rect(
                        block_size,
                        0,
                        display_drv.width - block_size,
                        display_drv.height,
                        colors[selected],
                    )
        elif e.button == 1:
            paint(x, y, colors[selected])
    elif e.type == Events.MOUSEMOTION and e.buttons[0] == 1:
        x, y = e.pos
        if (on_x_axis and y > block_size) or (not on_x_axis and x > block_size):
            paint(x, y, colors[selected])
    elif e.type == Events.QUIT:
        break
