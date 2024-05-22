from board_config import display_drv

palette = display_drv.get_palette(name="wheel", color_depth=16)

colors = [
    palette.BLACK,
    palette.WHITE,
    palette.RED,
    palette.PINK,
    palette.PURPLE,
    palette.DEEP_PURPLE,
    palette.INDIGO,
    palette.BLUE,
    palette.LIGHT_BLUE,
    palette.CYAN,
    palette.TEAL,
    palette.GREEN,
    palette.LIGHT_GREEN,
    palette.LIME,
    palette.YELLOW,
    palette.AMBER,
    palette.ORANGE,
    palette.DEEP_ORANGE,
    palette.BROWN,
    palette.GREY,
    palette.BLUE_GREY,
    
    palette.LIGHT_GREY,
    palette.DARK_GREY,
    palette.MAROON,
    palette.DEEP_PINK,
    palette.LIGHT_RED,
    palette.DARK_BLUE,
    palette.DARK_GREEN,
    palette.SALMON,
    palette.MAGENTA,
    palette.LIGHT_MAGENTA,
    palette.LIGHT_CYAN,
]

names = [
    "BLACK",
    "WHITE",
    "RED",
    "PINK",
    "PURPLE",
    "DEEP_PURPLE",
    "INDIGO",
    "BLUE",
    "LIGHT_BLUE",
    "CYAN",
    "TEAL",
    "GREEN",
    "LIGHT_GREEN",
    "LIME",
    "YELLOW",
    "AMBER",
    "ORANGE",
    "DEEP_ORANGE",
    "BROWN",
    "GREY",
    "BLUE_GREY",
    
    "LIGHT_GREY",
    "DARK_GREY",
    "MAROON",
    "DEEP_PINK",
    "LIGHT_RED",
    "DARK_BLUE",
    "DARK_GREEN",
    "SALMON",
    "MAGENTA",
    "LIGHT_MAGENTA",
    "LIGHT_CYAN",
]

line_height = 10

i = 0


def main():
    global i
    for color, name in zip(colors, names):
        if i >= display_drv.height:
            display_drv.vscsad((line_height + i) % display_drv.height)
        display_drv.fill_rect(
            0, i % display_drv.height, display_drv.width, line_height, color
        )
        display_drv.text(name, 0, (1 + i) % display_drv.height, ~color)
        i += line_height


def loop():
    while True:
        main()


main()
