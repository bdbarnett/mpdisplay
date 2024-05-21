from board_config import display_drv

palette = display_drv.get_palette(name="material_design", color_depth=16)
# palette = display_drv.get_palette(name="wheel", color_depth=16)

print(f"{palette.BLACK=:#0x}, {palette[0]=:#0x}; {palette.WHITE=:#0x}, {palette[-1]=:#0x}")

i = 0
while True:
    for color in palette:
        if i >= display_drv.height:
            display_drv.vscsad((1 + i - display_drv.height) % display_drv.height)
        display_drv.hline(0, i % display_drv.height, display_drv.width, color)
        i += 1
