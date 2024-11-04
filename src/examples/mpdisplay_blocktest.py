""" mpdisplay_simpletest.py """
from board_config import display_drv
from random import randint, getrandbits
from time import sleep
import gc


gc.collect()
# If byte swapping is required and the display bus is capable of having byte swapping disabled,
# disable it and set a flag so we can swap the color bytes as they are created.
if display_drv.requires_byte_swap:
    needs_swap = display_drv.disable_auto_byte_swap(True)
else:
    needs_swap = False


def main():
    block_width = 64
    block_height = 64

    max_x = display_drv.width - block_width - 1
    max_y = display_drv.height - block_height - 1

    print("Drawing blocks on display")
    # main loop
    while True:
        gc.collect()
        display_drv.fill_rect(
            randint(0, max_x),  # x position
            randint(0, max_y),  # y position
            block_width,  # width
            block_height,  # height
            getrandbits(16),  # color
        )

main()