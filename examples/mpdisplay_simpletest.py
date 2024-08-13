""" mpdisplay_simpletest.py """
from board_config import display_drv
import random
import asyncio
# If byte swapping is required and the display bus is capable of having byte swapping disabled,
# disable it and set a flag so we can swap the color bytes as they are created.
if display_drv.requires_byte_swap:
    needs_swap = display_drv.bus_swap_disable(True)
else:
    needs_swap = False

async def main():
    # Define the blocks
    bytes_per_pixel = 2
    block_width = 64
    block_height = 64
    block_bytes = block_width * block_height * bytes_per_pixel
    blocks = []

    # Maximum start positions of blocks
    max_x = display_drv.width - block_width - 1
    max_y = display_drv.height - block_height - 1

    # Create the blocks
    for pixel_color in [1 << (x + 8) | 1 << x for x in range(8)]:
        block = memoryview(bytearray(block_bytes))
        for i in range(0, block_bytes, bytes_per_pixel):
            block[i] = pixel_color & 0xFF
            block[i + 1] = pixel_color >> 8
        blocks.append(block)

    # main loop
    while True:
        display_drv.blit_rect(
            random.choice(blocks),  # buffer
            random.randint(0, max_x),  # x position
            random.randint(0, max_y),  # y position
            block_width,  # width
            block_height,  # height
        )
        await asyncio.sleep(0.001)

loop = asyncio.get_event_loop()
loop.create_task(main())
if hasattr(loop, "is_running") and loop.is_running():
    pass
else:
    loop.run_forever()
