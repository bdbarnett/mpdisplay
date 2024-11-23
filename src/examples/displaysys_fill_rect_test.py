""" displaysys_fill_rect_test.py """
from board_config import display_drv
from random import randint, getrandbits
import time
import gc


gc.collect()
# If byte swapping is required and the display bus is capable of having byte swapping disabled,
# disable it and set a flag so we can swap the color bytes as they are created.
if display_drv.requires_byteswap:
    needs_swap = display_drv.disable_auto_byteswap(True)
else:
    needs_swap = False


def main():
    block_size = 32

    max_x = display_drv.width - block_size - 1
    max_y = display_drv.height - block_size - 1

    print("Drawing blocks on display")
    count = 0
    start_time = time.time()
    while True:
        display_drv.fill_rect(
            randint(0, max_x),
            randint(0, max_y),
            block_size,
            block_size,
            getrandbits(16),
        )
        count += 1
        if count % 1000 == 0:
            print("blocks/sec:", count / (time.time() - start_time))

main()
