from board_config import display_drv

palette = display_drv.get_palette(name="material_design", color_depth=16)

families =[
    palette.red,
    palette.pink,
    palette.purple,
    palette.deep_purple,
    palette.indigo,
    palette.blue,
    palette.light_blue,
    palette.cyan,
    palette.teal,
    palette.green,
    palette.light_green,
    palette.lime,
    palette.yellow,
    palette.amber,
    palette.orange,
    palette.deep_orange,
    palette.brown,
    palette.grey,
    palette.blue_grey,
]

names =[
    "red",
    "pink",
    "purple",
    "deep_purple",
    "indigo",
    "blue",
    "light_blue",
    "cyan",
    "teal",
    "green",
    "light_green",
    "lime",
    "yellow",
    "amber",
    "orange",
    "deep_orange",
    "brown",
    "grey",
    "blue_grey",
]

line_height = 10

i = 0
def show_palette():
    global i
    for family in families:
        if i >= display_drv.height:
            display_drv.vscsad((line_height + i) % display_drv.height)
        for j, color in enumerate(family):
            display_drv.hline(0, (i + j) % display_drv.height, display_drv.width, color)
        display_drv.text(family._name, 0, (1 + i) % display_drv.height, ~family[0])
        i += line_height

while True:
    show_palette()
