""" display_simpletest.py """

from board_config import display_drv
from machine import Timer
import random
from sys import platform

# If the colors are incorrect, change this value.
# You may need to change the `reverse_bytes_in_word` value in board_config.py as well
swap_color_bytes = False

# Determine how buffers are allocated
alloc_buffer = lambda size: memoryview(bytearray(size))
# If heap_caps is available, use it to allocate in internal DMA-capable memory
if platform == "esp32":
    try:
        from heap_caps import malloc, CAP_DMA, CAP_INTERNAL  # For allocating buffers for the blocks and text
        alloc_buffer = lambda size: malloc(size, CAP_DMA | CAP_INTERNAL)
    except ImportError:
        pass

# Define RGB565 colors
BLACK = 0x0000
WHITE = 0xffff
MAGENTA = 0xf81f
CYAN = 0x07ff
YELLOW = 0xffe0
PURPLE = 0x780f
GREEN = 0x07e0
BLUE = 0x001f
RED = 0xf800
ORANGE = 0xfda0

# Define the blocks
bytes_per_pixel = 2
block_size = 64   # Size of each dimension in pixels
block_bytes = block_size * block_size * bytes_per_pixel
blocks = []
blocks_per_screen = (display_drv.width * display_drv.height) / (block_size * block_size)

# Create the blocks
for pixel_color in [BLACK, WHITE, MAGENTA, CYAN, YELLOW, PURPLE, GREEN, BLUE, RED, ORANGE]:
    block = alloc_buffer(block_bytes)
    for i in range(0, block_bytes, bytes_per_pixel):
        block[i] = pixel_color & 0xff if not swap_color_bytes else pixel_color >> 8
        block[i+1] = pixel_color >> 8 if not swap_color_bytes else pixel_color & 0xff
    blocks.append(block)

# Maximum start positions of blocks
max_x = display_drv.width - block_size - 1
max_y = display_drv.height - block_size - 1

# Counter and function to show blocks per second
block_count = 0
iter_count = 0
def print_count(_):
    global block_count, iter_count
    iter_count += 1
    print(f"\x08\x08\x08{(block_count // iter_count):3}", end ="")

# Prepare for the loop
print(f"{block_size}x{block_size} blocks per screen: {blocks_per_screen:.2f}")
print(f"Blocks per second:    ", end="")
tim = Timer(-1)
tim.init(mode=Timer.PERIODIC, freq=1, callback=print_count)

# Infinite loop
while True:
    display_drv.blit(
        random.randint(0, max_x),  # x position
        random.randint(0, max_y),  # y position
        block_size,                # width
        block_size,                # height
        random.choice(blocks))     # buffer
    block_count += 1
