""" display_simpletest.py """

from board_config import display_drv
import random

try:
    from time import ticks_ms, ticks_diff
except:
    from adafruit_ticks import ticks_ms, ticks_diff


# If byte swapping is required and the display bus is capable of having byte swapping disabled,
# disable it and set a flag so we can swap the color bytes as they are created.
if display_drv.requires_byte_swap:
    needs_swap = display_drv.bus_swap_disable(True)
else:
    needs_swap = False

# Define how buffers are allocated
alloc_buffer = lambda size: memoryview(bytearray(size))

# Define RGB565 colors
BLACK = 0x0000
WHITE = 0xFFFF
MAGENTA = 0xF81F
CYAN = 0x07FF
YELLOW = 0xFFE0
PURPLE = 0x780F
GREEN = 0x07E0
BLUE = 0x001F
RED = 0xF800
ORANGE = 0xFDA0

# Define the blocks
bytes_per_pixel = 2
block_width = 64
block_height = 64
block_bytes = block_width * block_height * bytes_per_pixel
blocks = []
blocks_per_screen = (display_drv.width * display_drv.height) // (
    block_width * block_height
)
# Create the blocks
# for pixel_color in [1 << (x + 8) | 1 << x for x in range(8)]:
for pixel_color in [
    BLACK,
    WHITE,
    MAGENTA,
    CYAN,
    YELLOW,
    PURPLE,
    GREEN,
    BLUE,
    RED,
    ORANGE,
]:
    block = alloc_buffer(block_bytes)
    for i in range(0, block_bytes, bytes_per_pixel):
        block[i] = pixel_color & 0xFF if not needs_swap else pixel_color >> 8
        block[i + 1] = pixel_color >> 8 if not needs_swap else pixel_color & 0xFF
    blocks.append(block)

# Maximum start positions of blocks
max_x = display_drv.width - block_width - 1
max_y = display_drv.height - block_height - 1

# Prepare for the loop
print(f"{block_width}x{block_height} blocks per screen: {blocks_per_screen}")
print(f"Blocks per second:     ", end="")


# Infinite loop
count = 0
start = ticks_ms()
while True:
    for _ in range(blocks_per_screen):
        display_drv.blit_rect(
            random.choice(blocks),  # buffer
            random.randint(0, max_x),  # x position
            random.randint(0, max_y),  # y position
            block_width,  # width
            block_height,
        )  # height
    count += blocks_per_screen
    elapsed = ticks_diff(ticks_ms(), start)
    print(f"\x08\x08\x08\x08{(count * 1000 // elapsed):4}", end="")
