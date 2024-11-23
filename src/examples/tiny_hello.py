"""
tiny_hello.py
=============

.. figure:: ../_static/tiny_hello.jpg
    :align: center

    Test text_font_converter on small displays.

Writes "Hello!" in a tiny font in random colors at random locations on the Display.

.. note:: This example requires the following modules:

  .. hlist::
    :columns: 3

    - `st7789py`
    - `tft_config`
    - `vga1_8x8`

"""

import random
import time
import tft_text
import tft_config

palette = tft_config.palette
import vga1_8x8 as font

tft = tft_config.config(tft_config.WIDE)


def center(text, fg=palette.WHITE, bg=palette.BLACK):
    """
    Centers the given text on the display.
    """
    length = len(text)
    tft_text.text(tft,
        font,
        text,
        tft.width // 2 - length // 2 * font.WIDTH,
        tft.height // 2 - font.HEIGHT,
        fg,
        bg,
    )


def main():
    """
    The big show!
    """
    for color in [palette.RED, palette.GREEN, palette.BLUE]:
        tft.draw.fill(color)
        tft.draw.rect(0, 0, tft.width, tft.height, palette.WHITE)
        center("Hello!", palette.WHITE, color)
        time.sleep(1)

    while True:
        for rotation in range(4):
            tft.rotation = rotation
            tft.draw.fill(0)
            col_max = tft.width - font.WIDTH * 6
            row_max = tft.height - font.HEIGHT

            for _ in range(128):
                tft_text.text(tft,
                    font,
                    "Hello!",
                    random.randint(0, col_max),
                    random.randint(0, row_max),
                    palette.color565(
                        random.getrandbits(8),
                        random.getrandbits(8),
                        random.getrandbits(8),
                    ),
                    palette.color565(
                        random.getrandbits(8),
                        random.getrandbits(8),
                        random.getrandbits(8),
                    ),
                )


main()
