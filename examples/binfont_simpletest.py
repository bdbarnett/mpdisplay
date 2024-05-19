"""
binfont_simpletest.py -- Simple test of the BinFont class.
inspired by Russ Hughes's hello.py

Draws on a framebuffer and blits it to the display.
"""

from board_config import display_drv
from tools import BinFont
import random
from framebuf import FrameBuffer, RGB565


BPP = display_drv.color_depth // 8  # Bytes per pixel


def write(font, text, x, y, fg_color, bg_color, scale):
    """
    Write text to the display.
    """
    buffer_width = font.font_width * scale * len(text)
    buffer_height = font.font_height * scale
    buffer = bytearray(buffer_width * buffer_height * BPP)
    fb = FrameBuffer(buffer, buffer_width, buffer_height, RGB565)
    fb.fill(bg_color)
    font.text(text, 0, 0, fb, fg_color, scale)
    display_drv.blit_rect(buffer, x, y, buffer_width, buffer_height)


def main():
    """
    The big show!
    """
    write_text = "Hello!"
    text_len = len(write_text)
    iterations = 1024

    font1 = BinFont("romfonts/vga_8x8.bin", 8, 8)
    font2 = BinFont("romfonts/vga_8x14.bin", 8, 14)
    font3 = BinFont("romfonts/vga_8x16.bin", 8, 16)
    fonts = [font1, font2, font3]

    max_width = max([font.font_width for font in fonts])
    max_height = max([font.font_height for font in fonts])

    while True:
        for rotation in range(4):
            scale = rotation + 1
            display_drv.rotation = rotation * 90
            width, height = display_drv.width, display_drv.height
            # display_drv.fill_rect(0, 0, width, height, 0x0000)

            col_max = width - max_width * scale * text_len
            row_max = height - max_height * scale
            if col_max < 0 or row_max < 0:
                raise RuntimeError("This font is too big to display on this screen.")

            for _ in range(iterations // scale):
                write(
                    fonts[random.randint(0, 1)],
                    write_text,
                    random.randint(0, col_max),
                    random.randint(0, row_max),
                    display_drv.color565(
                        random.getrandbits(8),
                        random.getrandbits(8),
                        random.getrandbits(8),
                    ),
                    display_drv.color565(
                        random.getrandbits(8),
                        random.getrandbits(8),
                        random.getrandbits(8),
                    ),
                    scale,
                )


main()
