"""displaysys_block_test.py"""

from board_config import display_drv
import random
import time
import gc


gc.collect()
# If byte swapping is required and the display bus is capable of having byte swapping disabled,
# disable it and set a flag so we can swap the color bytes as they are created.
if display_drv.requires_byteswap:
    needs_swap = display_drv.disable_auto_byteswap(True)
else:
    needs_swap = False


def test():
    raise Exception("Test exception")


def main():
    # display_bus.register_callback(test)
    block_size = 32
    blocks = []

    max_x = display_drv.width - block_size - 1
    max_y = display_drv.height - block_size - 1

    for pixel_color in [0x0000, 0xFFFF, 0xF800, 0x07E0, 0x001F, 0xFFE0, 0x07FF, 0xF81F]:
        pixel_bytes = (
            pixel_color.to_bytes(2, "big") if needs_swap else pixel_color.to_bytes(2, "little")
        )
        blocks.append(memoryview(bytearray(pixel_bytes * (block_size * block_size))))

    print("Drawing blocks on display")
    count = 0
    start_time = time.time()
    while True:
        display_drv.blit_rect(
            random.choice(blocks),
            random.randint(0, max_x),
            random.randint(0, max_y),
            block_size,
            block_size,
        )
        count += 1
        if count % 2000 == 0:
            print(f"\rblocks/sec: {(count / (time.time() - start_time)):5.2f}", end="")


main()
