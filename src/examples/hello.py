"""
hello.py
========

.. figure:: ../_static/hello.jpg
    :align: center

    Test for text_font_converter.

Writes "Hello!" in random colors at random locations on the Display.
https://www.youtube.com/watch?v=atBa0BYPAAc

.. note:: This example requires the following modules:

  .. hlist::
    :columns: 3

    - `st7789py`
    - `tft_config`
    - `vga2_bold_16x32`

"""

import random

import tft_config
import tft_text
import vga2_bold_16x32 as font

palette = tft_config.palette


def main():
    """
    The big show!
    """
    tft = tft_config.config(tft_config.WIDE)

    while True:
        for rotation in range(4):
            tft.rotation = rotation
            tft.draw.fill(0)
            col_max = tft.width - font.WIDTH * 5
            row_max = tft.height - font.HEIGHT
            if col_max < 0 or row_max < 0:
                raise RuntimeError("This font is too big to display on this screen.")

            for _ in range(100):
                tft_text.text(tft,
                    font,
                    "Hello",
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
