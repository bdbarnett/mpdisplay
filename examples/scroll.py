"""
scroll.py
=========

.. figure:: ../_static/scroll.jpg
    :align: center

    Test for hardware scrolling.

Smoothly scrolls all font characters up the screen.
Only works with fonts with heights that are even multiples of the screen height,
(i.e. 8 or 16 pixels high)

.. note:: This example requires the following modules:

  .. hlist::
    :columns: 3

    - `st7789py`
    - `tft_config`
    - `vga2_bold_16x16`

"""

import utime
import random

import tft_config

pallette = tft_config.Pallette
import vga2_bold_16x16 as font


def main():
    """main"""
    tft = tft_config.config(tft_config.SCROLL)
    last_line = tft.height - font.HEIGHT
    tfa = tft_config.TFA  # top free area when scrolling
    bfa = tft_config.BFA  # bottom free area when scrolling
    tft.vscrdef(tfa, 240, bfa)

    tft.fill(pallette.BLUE)
    scroll = 0
    character = 0
    col = tft.width // 2 - 5 * font.WIDTH // 2

    while True:
        tft.fill_rect(0, scroll, tft.width, 1, pallette.BLUE)

        if scroll % font.HEIGHT == 0:
            tft.text(
                font,
                f"x{character:02x} {chr(character)}",
                col,
                (scroll + last_line) % tft.height,
                pallette.WHITE,
                pallette.BLUE,
            )

            character = character + 1 if character < 256 else 0

        tft.vscsad(scroll + tfa)
        scroll += 1

        if scroll == tft.height:
            scroll = 0

        utime.sleep(0.01)


main()
