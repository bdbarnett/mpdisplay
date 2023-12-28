""" display_simpletest"""

from board_config import display_drv
import random

try:
    from heap_caps import malloc, CAP_DMA, CAP_INTERNAL  # For allocating buffers for the blocks and text
    create_buffer = lambda size: malloc(size, CAP_DMA | CAP_INTERNAL)
except:
    create_buffer = lambda size: bytearray(size)

# If the are incorrect, change this value.
# You may need to change the `reverse_bytes_in_word` value in board_config.py as well
swap_color_bytes = False

# Get the display dimensions
display_width = display_drv.width
display_height = display_drv.height

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
block_size = 64   # Size of each dimension in pixels
block_pixels = block_size * block_size
blocks = []
# for color in [random.randint(0, 65535)] * 10:
for pixel_color in [BLACK, WHITE, MAGENTA, CYAN, YELLOW, PURPLE, GREEN, BLUE, RED, ORANGE]:
    block = create_buffer(block_pixels*2)
    for i in range(block_pixels):
        block[i*2] = pixel_color & 0xff if not swap_color_bytes else pixel_color >> 8
        block[i*2+1] = pixel_color >> 8 if not swap_color_bytes else pixel_color & 0xff
    blocks.append(block)

# Infinite loop
while True:
    buffer = random.choice(blocks)
    x = random.randint(0, display_width-block_size-1)
    y = random.randint(0, display_height-block_size-1)
    display_drv.blit(x, y, block_size, block_size, buffer)
