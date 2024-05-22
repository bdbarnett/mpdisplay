from board_config import display_drv

palette = display_drv.get_palette(name="ega", color_depth=16)

colors = {
    palette.BLACK: "Black",
    palette.BLUE: "Blue",
    palette.GREEN: "Green",
    palette.CYAN: "Cyan",
    palette.RED: "Red",
    palette.MAGENTA: "Magenta",
    palette[6]: "",
    palette.LIGHT_GREY: "Light Grey",
    palette.DARK_BLUE: "Dark Blue",
    palette[9]: "",
    palette[10]: "",
    palette[11]: "",
    palette[12]: "",
    palette[13]: "",
    palette[14]: "",
    palette[15]: "",
    palette.DARK_GREEN: "Dark Green",
    palette.BLUE_GREY: "Blue Grey",
    palette[18]: "",
    palette[19]: "",
    palette.BROWN: "Brown",
    palette[21]: "",
    palette[22]: "",
    palette[23]: "23",
    palette.TEAL: "",
    palette[25]: "",
    palette[26]: "",
    palette[27]: "",
    palette[28]: "",
    palette.INDIGO: "Indigo",
    palette[30]: "",
    palette[31]: "",
    palette[32]: "",
    palette[33]: "",
    palette.LIME: "Lime",
    palette[35]: "",
    palette[36]: "",
    palette[37]: "",
    palette.ORANGE: "Orange",
    palette.SALMON: "Salmon",
    palette.DEEP_PURPLE: "Deep Purple",
    palette.PURPLE: "Purple",
    palette[42]: "",
    palette[43]: "",
    palette[44]: "",
    palette.DEEP_PINK: "Deep Pink",
    palette.AMBER: "Amber",
    palette.PINK: "Pink",
    palette.GREY: "Grey",
    palette[49]: "",
    palette[50]: "",
    palette[51]: "",
    palette.DEEP_ORANGE: "Deep Orange",
    palette[53]: "",
    palette[54]: "",
    palette[55]: "",
    palette.DARK_GREY: "Dark Grey",
    palette.LIGHT_BLUE: "Light Blue",
    palette.LIGHT_GREEN: "Light Green",
    palette.LIGHT_CYAN: "Light Cyan",
    palette.LIGHT_RED: "Light Red",
    palette.LIGHT_MAGENTA: "Light Magenta",
    palette.YELLOW: "Yellow",
    palette.WHITE: "White",
}

line_height = 10

i = 0

def main():
    global i
    for index in range(32):
        color_a = list(colors.keys())[index]
        name_a = f"{index} {colors[color_a]}"
        color_b = list(colors.keys())[index + 32]
        name_b = f"{index+32} {colors[color_b]}"
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
