"""
gui_simpletest.py - Simple test program for gui_framework.py
"""

from color_setup import ssd
from time import ticks_ms, ticks_diff
from array import array  # for creating a polygon


# Define colors (max 16 colors if using lookup tables / GS4_HMSB mode)
# Note:  ssd.color and ssd.colors_registered should not be used with Nano-GUI or
# Micro-GUI because those packages have their own mechanisms for managing colors.
BLACK = ssd.color(0, 0, 0)
GREEN = ssd.color(0, 255, 0)
RED = ssd.color(255, 0, 0)
BLUE = ssd.color(0, 0, 255)
YELLOW = ssd.color(255, 255, 0)
MAGENTA = ssd.color(255, 0, 255)
CYAN = ssd.color(0, 255, 255)
WHITE = ssd.color(255, 255, 255)
GRAY = ssd.color(96, 96, 96)
GRAY = ssd.color(128, 128, 128, GRAY)  # Example of how to redefine a color in the lookup table
print(f"{ssd.colors_registered} colors registered.  (Will be 0 if not using lookup tables / GS4_HMSB mode.)")

# Clear the display and draw some shapes using framebuf.FrameBuffer methods
ssd.fill(BLACK)
ssd.poly(0, ssd.height - 1, array('h', [0, 0, ssd.width // 2, -ssd.height // 4, ssd.width, 0]), MAGENTA, True)  # Magenta triangle at bottom
ssd.line(0, 0, ssd.width - 1, ssd.height - 1, GREEN)  # Green diagonal corner-to-corner
ssd.rect(0, 0, 15, 15, RED, True)  # Red square at top left
ssd.rect(ssd.width -15, ssd.height -15, 15, 15, BLUE, True)  # Blue square at bottom right
ssd.hline(ssd.width // 8, ssd.height // 2, ssd.width * 3 // 4, YELLOW)  # Yellow horizontal line at center
ssd.vline(ssd.width // 2, ssd.height // 4, ssd.height // 2, CYAN)  # Cyan vertical line at center
ssd.ellipse(ssd.width // 2, ssd.height // 2, ssd.width // 4, ssd.height // 8, WHITE, True)  # White ellipse at center
ssd.text("MPDisplay", (ssd.width - 72) // 2, ssd.height // 2, BLACK)  # White text centered
ssd.pixel(ssd.width // 2, ssd.height *7 // 8, BLACK)  # Black pixel at center of triangle

# Measure the time to update the display
start = ticks_ms()
ssd.show()
stop = ticks_ms()
print(f"Time to update display:  {ticks_diff(stop, start)} ms")
