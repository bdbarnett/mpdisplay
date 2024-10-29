from board_config import display_drv
from pygraphics.palettes import get_palette
from pygraphics.binfont import text16

# If byte swapping is required and the display bus is capable of having byte swapping disabled,
# disable it and set a flag so we can swap the color bytes as they are created.
if display_drv.requires_byte_swap:
    needs_swap = display_drv.disable_auto_byte_swap(True)
else:
    needs_swap = False

display_drv.rotation = 0

palette = get_palette(name="material_design", color_depth=16, swapped=needs_swap)

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

line_height = 30

i = 0
def main():
    global i
    for family in families:
        if i >= display_drv.height:
            display_drv.vscsad((line_height + i) % display_drv.height)
        for j, color in enumerate(family):
            display_drv.fill_rect(0, (i + j*3) % display_drv.height, display_drv.width, 3, color)
        text16(display_drv, family._name, 0, (1 + i) % display_drv.height, palette.BLACK)
        i += line_height

def loop():
    while True:
        main()

main()