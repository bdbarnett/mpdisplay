from board_config import display_drv

# If byte swapping is required and the display bus is capable of having byte swapping disabled,
# disable it and set a flag so we can swap the color bytes as they are created.
if display_drv.requires_byte_swap:
    needs_swap = display_drv.bus_swap_disable(True)
else:
    needs_swap = False

palette = display_drv.get_palette(name="wheel", color_depth=16, swapped=needs_swap)

colors = [
    palette.AMBER,
    palette.AZURE,
    palette.BLACK,
    palette.BLUE,
    palette.BLUE_GREY,
    palette.BROWN,
    palette.CYAN,
    palette.DARK_BLUE,
    palette.DARK_GREY,
    palette.DARK_RED,
    palette.GREEN,
    palette.GREY,
    palette.INDIGO,
    palette.LIGHT_BLUE,
    palette.LIGHT_CYAN,
    palette.LIGHT_GREEN,
    palette.LIGHT_GREY,
    palette.LIGHT_MAGENTA,
    palette.LIGHT_RED,
    palette.LIGHT_YELLOW,
    palette.LIME,
    palette.MAGENTA,
    palette.OLIVE,
    palette.ORANGE,
    palette.PINK,
    palette.PURPLE,
    palette.RED,
    palette.ROSE,
    palette.SALMON,
    palette.SKY_BLUE,
    palette.SPRING_GREEN,
    palette.TEAL,
    palette.WHITE,
    palette.YELLOW,
]

names = [
    "Amber",
    "Azure",
    "Black",
    "Blue",
    "Blue Grey",
    "Brown",
    "Cyan",
    "Dark Blue",
    "Dark Grey",
    "Dark Red",
    "Green",
    "Grey",
    "Indigo",
    "Light Blue",
    "Light Cyan",
    "Light Green",
    "Light Grey",
    "Light Magenta",
    "Light Red",
    "Light Yellow",
    "Lime",
    "Magenta",
    "Olive",
    "Orange",
    "Pink",
    "Purple",
    "Red",
    "Rose",
    "Salmon",
    "Sky Blue",
    "Spring Green",
    "Teal",
    "White",
    "Yellow",
]

line_height = 18

i = 0

def main():
    global i
    for color, name in zip(colors, names):
        if i >= display_drv.height:
            display_drv.vscsad((line_height + i) % display_drv.height)
        display_drv.fill_rect(
            0, i % display_drv.height, display_drv.width, line_height, color
        )
        display_drv.btext(name, 0, (1 + i) % display_drv.height, ~color)
        i += line_height


def loop():
    while True:
        main()


main()
