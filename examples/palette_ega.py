from board_config import display_drv

# If byte swapping is required and the display bus is capable of having byte swapping disabled,
# disable it and set a flag so we can swap the color bytes as they are created.
if display_drv.requires_byte_swap:
    needs_swap = display_drv.bus_swap_disable(True)
else:
    needs_swap = False

palette = display_drv.get_palette(name="ega", color_depth=16, swapped=needs_swap)

line_height = max([display_drv.height // (len(palette) // 2), 10])

i = 0

def main():
    global i
    for index in range(32):
        color_a = palette[index]
        name_a = f"{index} "
        if index in palette.names:
            name_a += palette.names[index]
        color_b = palette[index + 32]
        name_b = f"{index+32} "
        if index + 32 in palette.names:
            name_b += palette.names[index + 32]
        if i >= display_drv.height:
            display_drv.vscsad((line_height + i) % display_drv.height)
        display_drv.fill_rect(0, i % display_drv.height, display_drv.width//2, line_height, color_a)
        display_drv.fill_rect(display_drv.width//2, i % display_drv.height, display_drv.width//2, line_height, color_b)
        display_drv.text(name_a, 0, (1 + i) % display_drv.height, ~color_a)
        display_drv.text(name_b, display_drv.width//2, (1 + i) % display_drv.height, ~color_b)
        i += line_height


def loop():
    while True:
        main()


main()
