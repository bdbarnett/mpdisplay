from board_config import display_drv

palette = display_drv.get_palette(name="wheel", color_depth=16)

colors =[
    palette.BLACK,
    palette.DARK_BLUE,
    palette.BLUE,
    palette.DARK_GREEN,
    palette.TEAL,
    palette.LIGHT_BLUE,
    palette.GREEN,
    palette.SPRING_GREEN,
    palette.CYAN,
    palette.DARK_RED,
    palette.PURPLE,
    palette.INDIGO,
    palette.OLIVE,
    palette.GRAY,
    palette.LIGHT_PURPLE,
    palette.LIME,
    palette.LIGHT_GREEN,
    palette.LIGHT_CYAN,
    palette.RED,
    palette.DEEP_PINK,
    palette.MAGENTA,
    palette.ORANGE,
    palette.SALMON,
    palette.PINK,
    palette.YELLOW,
    palette.LIGHT_YELLOW,
    palette.WHITE,
    palette.DARK_GRAY,
    palette.LIGHT_GRAY,
    palette.BROWN,
    palette.TAN,
    palette.GOLD,
]

names =[
    "BLACK",
    "DARK_BLUE",
    "BLUE",
    "DARK_GREEN",
    "TEAL",
    "LIGHT_BLUE",
    "GREEN",
    "SPRING_GREEN",
    "CYAN",
    "DARK_RED",
    "PURPLE",
    "INDIGO",
    "OLIVE",
    "GRAY",
    "LIGHT_PURPLE",
    "LIME",
    "LIGHT_GREEN",
    "LIGHT_CYAN",
    "RED",
    "DEEP_PINK",
    "MAGENTA",
    "ORANGE",
    "SALMON",
    "PINK",
    "YELLOW",
    "LIGHT_YELLOW",
    "WHITE",
    "DARK_GRAY",
    "LIGHT_GRAY",
    "BROWN",
    "TAN",
    "GOLD",
]

line_height = 10

i = 0
def show_palette():
    global i
    for color, name in zip(colors, names):
        if i >= display_drv.height:
            display_drv.vscsad((line_height + i) % display_drv.height)
        display_drv.fill_rect(0, i % display_drv.height, display_drv.width, line_height, color)
        display_drv.text(name, 0, (1 + i) % display_drv.height, ~color)
        i += line_height

while True:
    show_palette()
