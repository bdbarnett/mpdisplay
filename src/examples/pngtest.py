import png
from board_config import display_drv
from pygraphics.palettes.shades import ShadesPalette
from pydevices.displaybuf import DisplayBuffer
from collections import namedtuple
from time import sleep
import os


png_image = namedtuple("png_image", ["width", "height", "pixels", "metadata"])

# iterator to recursively find all .png files in a directory
def png_files(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".png"):
                yield os.path.join(root, file)

png_path = "/home/brad/gh2/material-design-icons/png/"
bg_color = 0x000F

canvas = DisplayBuffer(display_drv)
canvas.fill(bg_color)
canvas.show()
pal = ShadesPalette(rgb=(255, 255, 255))

while True:
    for file_name in png_files(png_path):
        p = png_image(*png.Reader(filename=file_name).read())
        if not p.metadata["greyscale"] or p.metadata['bitdepth'] != 8:
            print(f"Only 8-bit PNGs are supported {file_name}")
            continue
        pos_x, pos_y = (canvas.width - p.width) // 2, (canvas.height - p.height) // 2
        offset = 1 if p.metadata["alpha"] else 0
        planes = p.metadata["planes"]
        buf = memoryview(bytearray(p.width * p.height * 2))
        for y, row in enumerate(p.pixels):
            for x in range(0, p.width):
                if row[x*planes+offset] != 0:
                    buf[(y*p.width + x)*2:(y*p.width + x)*2+2] = pal[row[x*planes+offset]].to_bytes(2, 'little')
                    # canvas.pixel(pos_x + x, pos_y + y, pal[row[x*planes+offset]])
                else:
                    buf[(y*p.width + x)*2:(y*p.width + x)*2+2] = bg_color.to_bytes(2, 'little')
                    # canvas.pixel(pos_x + x, pos_y + y, bg_color)
        canvas.blit_rect(buf, pos_x, pos_y, p.width, p.height)
        lines = os.path.relpath(file_name, png_path).rpartition("/")
        canvas.text16(lines[0] + "/", 0, 0, 0xFFFF)
        canvas.text16("    " + lines[2], 0, 16, 0xFFFF)
        canvas.show()
        sleep(1)
        canvas.fill_rect(pos_x, pos_y, p.width, p.height, bg_color)
        canvas.fill_rect(0, 0, canvas.width, 32, bg_color)
