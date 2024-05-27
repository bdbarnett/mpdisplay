from board_config import display_drv

# If byte swapping is required and the display bus is capable of having byte swapping disabled,
# disable it and set a flag so we can swap the color bytes as they are created.
if display_drv.requires_byte_swap:
    needs_swap = display_drv.bus_swap_disable(True)
else:
    needs_swap = False

palette = display_drv.get_palette(name="cube", size=5, color_depth=16, swapped=needs_swap)
# palette = display_drv.get_palette(name="wheel", length=522, color_depth=16, swapped=needs_swap)

line_height = 20
last_line = display_drv.height - line_height
scroll = 0
y = 0
def main():
    global y, scroll
    for index, color in enumerate(palette):
        if y - scroll - last_line > 0:
            scroll = (y - last_line) % display_drv.height
            display_drv.vscsad(scroll)
        name = f"{index} - {palette.color_name(index)}"
        text_color = palette.WHITE if palette.brightness(index) < 0.4 else palette.BLACK
        display_drv.fill_rect(0, y % display_drv.height, display_drv.width, line_height, color)
        display_drv.btext(name, 2, (y + 2) % display_drv.height, text_color)
        y += line_height


def loop():
    while True:
        main()


main()
