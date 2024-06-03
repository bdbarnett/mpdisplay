from board_config import display_drv
from bmp565 import BMP565
from time import sleep
from random import choice
from collections import namedtuple


image = BMP565("assets/world-1.bmp", streamed=True)
print(f"\n{image.width=}, {image.height=}, {image.bpp=}")


def draw_bg(dest_x, dest_y, source_x, source_y, source_image=image, width=image.width, height=1):
    display_drv.blit_rect(source_image[source_x:source_x + width, source_y:source_y + height], dest_x, dest_y, width, height)

draw_bg(0, 0, 0, 0, height=display_drv.height)
sleep(3)

i = display_drv.height
while True:
    display_drv.vscsad(i % display_drv.height)
    draw_bg(0, i % display_drv.height, 0, i % image.height)
    i += 1
