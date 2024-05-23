from board_config import display_drv

palette = display_drv.get_palette(name="wheel", color_depth=16, length=256, saturation=1.0)
# palette = display_drv.get_palette(name="wheel", color_depth=16, length=256)

line_height = 2

i = 0
def main():
    global i
    for color in palette:
        if i >= display_drv.height:
            display_drv.vscsad((line_height + i) % display_drv.height)
        display_drv.fill_rect(0, i % display_drv.height, display_drv.width, line_height, color)
        i += line_height

def loop():
    while True:
        main()

loop()