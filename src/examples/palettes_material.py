from board_config import display_drv
from palettes import get_palette
from graphics import text16

# If byte swapping is required and the display bus is capable of having byte swapping disabled,
# disable it and set a flag so we can swap the color bytes as they are created.
if display_drv.requires_byteswap:
    needs_swap = display_drv.disable_auto_byteswap(True)
else:
    needs_swap = False

display_drv.rotation = 0

palette = get_palette(name="material_design", color_depth=16, swapped=needs_swap)

def main():
    line_height=1
    for i, color in enumerate(palette):
        display_drv.fill_rect(0, i*line_height, display_drv.width, line_height, color)

while True:
    main()
