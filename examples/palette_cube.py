from board_config import display_drv

# If byte swapping is required and the display bus is capable of having byte swapping disabled,
# disable it and set a flag so we can swap the color bytes as they are created.
if display_drv.requires_byte_swap:
    needs_swap = display_drv.bus_swap_disable(True)
else:
    needs_swap = False

palette = display_drv.get_palette(name="cube", size=3, color_depth=16, swapped=needs_swap)

line_height = 18

y = 0
def main():
    global y
    for index, color in enumerate(palette):
        name = f"{index} - {palette.color_name(index)}"
        if y + line_height >= display_drv.height:
            display_drv.vscsad((y + line_height) % display_drv.height)
        display_drv.fill_rect(0, y % display_drv.height, display_drv.width, line_height, color)
        display_drv.btext(name, 0, (y + 1) % display_drv.height, ~color)
        y += line_height


def loop():
    while True:
        main()


main()
