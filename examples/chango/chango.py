"""
chango.py
=========

.. figure:: ../_static/chango.jpg
    :align: center

    Test for TrueType write_font_converter.

See the :ref:`write_font_converter.py<write_font_converter>` program in the utils directory.

.. note:: This example requires the following modules:

  .. hlist::
    :columns: 3

    - `st7789py`
    - `tft_config`
    - `chango_16`
    - `chango_32`
    - `chango_64`

"""

import gc
import chango_16 as font_16
import chango_32 as font_32
import chango_64 as font_64
import tft_config

palette = tft_config.Palette

gc.collect()


def main():
    """main"""
    # enable display and clear screen
    tft = tft_config.config(tft_config.WIDE)

    row = 0
    tft.write(font_16, "abcdefghijklmnopqrst", 0, row, palette.RED)
    row += font_16.HEIGHT

    tft.write(font_32, "abcdefghij", 0, row, palette.GREEN)
    row += font_32.HEIGHT

    tft.write(font_64, "abcd", 0, row, palette.BLUE)
    row += font_64.HEIGHT


main()
