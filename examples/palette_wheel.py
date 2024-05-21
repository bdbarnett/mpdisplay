from board_config import display_drv

palette = display_drv.get_palette(name="wheel", color_depth=16)

line_height = 2

i = 0
def show_palette():
    global i
    for color in palette:
        if i >= display_drv.height:
            display_drv.vscsad((line_height + i) % display_drv.height)
        display_drv.fill_rect(0, i % display_drv.height, display_drv.width, line_height, color)
        i += line_height

while True:
    show_palette()
