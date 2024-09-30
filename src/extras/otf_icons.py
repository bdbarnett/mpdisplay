"""
Creates mono custom icons on-the-fly using the pbm module.
"""
from pbm import PBM
from gfx import shapes


# Dictionary of icon names and list of their drawing functions

_icons = {
    "up_arrow": [lambda c: shapes.triangle(c, 0, c.height*3//4, c.width//2, c.height//4, c.width-1, c.height*3//4, 1, True)],
    "down_arrow": [lambda c: shapes.triangle(c, 0, c.height//4, c.width//2, c.height*3//4, c.width-1, c.height//4, 1, True)],
    "left_arrow": [lambda c: shapes.triangle(c, c.width*3//4, 0, c.width//4, c.height//2, c.width*3//4, c.height-1, 1, True)],
    "right_arrow": [lambda c: shapes.triangle(c, c.width//4, 0, c.width*3//4, c.height//2, c.width//4, c.height-1, 1, True)],
    "up_down_arrow": [lambda c: shapes.triangle(c, 0, c.height*7//16, c.width//2, 0, c.width-1, c.height*7//16, 1, True),
                      lambda c: shapes.triangle(c, 0, c.height*9//16, c.width//2, c.height-1, c.width-1, c.height*9//16, 1, True)],
    "left_right_arrow": [lambda c: shapes.triangle(c, c.width*7//16, 0, 0, c.height//2, c.width*7//16, c.height-1, 1, True),
                         lambda c: shapes.triangle(c, c.width*9//16, 0, c.width-1, c.height//2, c.width*9//16, c.height-1, 1, True)],
    "plus": [lambda c: shapes.fill_rect(c, c.width//16, c.height*3//8, c.width*7//8, c.height//4, 1),
             lambda c: shapes.fill_rect(c, c.width*3//8, c.height//16, c.width//4, c.height*7//8, 1)],
    "minus": [lambda c: shapes.fill_rect(c, c.width//16, c.height*3//8, c.width*7//8, c.height//4, 1)],
    "circle": [lambda c: shapes.circle(c, c.width//2, c.height//2, c.width*7//16, 1, True)],
    "square": [lambda c: shapes.fill_rect(c, c.width//16, c.height//16, c.width*7//8, c.height*7//8, 1)],
    "triangle": [lambda c: shapes.triangle(c, 0, c.height*15//16, c.width//2, c.height//8, c.width-1, c.height*15//16, 1, True)],
    "diamond": [lambda c: shapes.triangle(c, c.width//2, c.height//16, c.width//8, c.height//2, c.width//2, c.height*15//16, 1, True),
                lambda c: shapes.triangle(c, c.width//2, c.height//16, c.width*7//8, c.height//2, c.width//2, c.height*15//16, 1, True)],
    "heart": [lambda c: shapes.circle(c, c.width*5//16, c.height*5//16, c.width*5//16, 1, True),
              lambda c: shapes.circle(c, c.width*11//16, c.height*5//16, c.width*5//16, 1, True),
              lambda c: shapes.triangle(c, 0, c.height*3//8, c.width//2, c.height-1, c.width-1, c.height*3//8, 1, True)],
    "smiley": [lambda c: shapes.circle(c, c.width//2, c.height//2, c.width//2, 1, True),
               lambda c: shapes.circle(c, c.width//3, c.height//3, c.width//8, 0, True),
               lambda c: shapes.circle(c, c.width//3*2, c.height//3, c.width//8, 0, True),
               lambda c: shapes.arc(c, c.width//2, c.height//2, c.width//3, 15, 165, 0)],
    "frown": [lambda c: shapes.circle(c, c.width//2, c.height//2, c.width//2, 1, True),
              lambda c: shapes.circle(c, c.width//3, c.height//3, c.width//8, 0, True),
              lambda c: shapes.circle(c, c.width//3*2, c.height//3, c.width//8, 0, True),
              lambda c: shapes.arc(c, c.width//2, c.height*5//6, c.width//4, 210, 330, 0)],
    "radio_button_unchecked": [lambda c: shapes.circle(c, c.width//2, c.height//2, c.width//2, 1, True),
                               lambda c: shapes.circle(c, c.width//2, c.height//2, c.width*3//8, 0, True)],
    "radio_button_checked": [lambda c: shapes.circle(c, c.width//2, c.height//2, c.width//2, 1, True),
                             lambda c: shapes.circle(c, c.width//2, c.height//2, c.width*3//8, 0, True),
                             lambda c: shapes.circle(c, c.width//2, c.height//2, c.width//4, 1, True)],
    "checkbox_unchecked": [lambda c: shapes.fill_rect(c, 0, 0, c.width-1, c.height-1, 1),
                           lambda c: shapes.fill_rect(c, c.width//8, c.height//8, c.width*3//4-1, c.height*3//4-1, 0)],
    "checkbox_checked": [lambda c: shapes.fill_rect(c, 0, 0, c.width-1, c.height-1, 1),
                         lambda c: shapes.fill_rect(c, c.width//8, c.height//8, c.width*3//4-1, c.height*3//4-1, 0),
                         lambda c: shapes.fill_rect(c, c.width//4, c.height//4, c.width//2-1, c.height//2-1, 1)],
}


def otf_icon(icon_name, w=16, h=16):
    """
    Create a custom icon on-the-fly.

    :param icon_name: The name of the icon to create.
    :param w: The width of the icon.
    :param h: The height of the icon.
    :return: A PBM object containing the icon.
    """
    if icon_name not in _icons:
        raise ValueError("Invalid icon name")
    icon = PBM(width=w, height=h)
    for draw_func in _icons[icon_name]:
        draw_func(icon)
    return icon


# Example usage:
def main():
    from board_config import display_drv
    from framebuf import FrameBuffer, RGB565

    display_drv.fill(0xF800)
    current_x = 0
    current_y = 0
    icon_size = 64
    for i, icon_name in enumerate(_icons):
        if current_x + icon_size > display_drv.width:
            current_x = 0
            current_y += icon_size
        print(f"Drawing icon {icon_name} at ({current_x}, {current_y}):  ", end="")
        try:
            icon = otf_icon(icon_name, icon_size, icon_size)
            buf = bytearray(icon.width * icon.height * 2)
            fb = FrameBuffer(buf, icon.width, icon.height, RGB565)
            icon.render(fb, 0, 0, 0xFFFF)
            display_drv.blit_transparent(buf, current_x, current_y, icon.width, icon.height, 0x0)
            print("OK")
        except Exception as e:
            print(e)
        current_x += icon_size

main()
