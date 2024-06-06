"""
Use the BMP565 class to save a screenshot of the display to a BMP565 file.
"""
from color_setup import ssd
from bmp565 import BMP565
import displaybuf_simpletest

bmp = BMP565(source=ssd.buffer, width=ssd.width, height=ssd.height)
filename = bmp.save("screenshot.bmp")
print(f"\nSaved BMP565 file as '{filename}'")