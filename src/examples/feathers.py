"""
feathers.py
===========
Modified by Brad Barnett from Russ Hughes's original to scroll vertically instead of horizontally
and to use palettes.wheel.WheelPalette for deeper colors from HSV instead of RGB.

.. figure:: ../_static/feathers.jpg
    :align: center

    Test hardware scrolling.

Smoothly scrolls mirrored rainbow colored random curves across the display.

.. note:: This example requires the following modules:

  .. hlist::
    :columns: 3

    - `palettes`
    - `tft_config`

"""

import random
import math
import time

import tft_config
from pygraphics.palettes.wheel import WheelPalette



def between(left, right, along):
    """returns a point along the curve from left to right"""
    dist = (1 - math.cos(along * math.pi)) / 2
    return left * (1 - dist) + right * dist


def main():
    """
    The big show!
    """
    # enable display and clear screen

    tft = tft_config.config(tft_config.FEATHERS)

    # If byte swapping is required and the display bus is capable of having byte swapping disabled,
    # disable it and set a flag so we can swap the color bytes as they are created.
    if tft.requires_byte_swap:
        needs_swap = tft.disable_auto_byte_swap(True)
    else:
        needs_swap = False

    palette = WheelPalette(swapped=needs_swap, saturation=1.0)

    height = tft.height  # height of display in pixels
    width = tft.width  # width if display in pixels

    tfa = tft_config.TFA  # left free area when scrolling
    bfa = tft_config.BFA  # right free area when scrolling

    scroll = 0  # scroll position
    wheel = 0  # color wheel position

    tft.vscrdef(tfa, height, bfa)  # set scroll area
    tft.vscsad(scroll + tfa)  # set scroll position
    tft.draw.fill(palette.BLACK)  # clear screen

    half = (width >> 1) - 1  # half the width of the display
    interval = 0  # steps between new points
    increment = 0  # increment per step
    counter = 1  # step counter, overflow to start
    current_x = 0  # current_x value
    last_x = 0  # last_x value

    # segment offsets
    y_offsets = [i * (height // 8) - 1 for i in range(2, 9)]

    while True:
        # when the counter exceeds the interval, save current_x to last_x,
        # choose a new random value for current_x between 0 and 1/2 the
        # width of the display, choose a new random interval then reset
        # the counter to 0

        if counter > interval:
            last_x = current_x
            current_x = random.randint(0, half)
            counter = 0
            interval = random.randint(10, 100)
            increment = 1 / interval  # increment per step

        # clear the first row of the display and scroll it
        tft.draw.hline(0, scroll, width, palette.BLACK)
        tft.vscsad(scroll + tfa)

        # get the next point between last_x and current_x
        tween = int(between(last_x, current_x, counter * increment))

        # draw mirrored pixels across the display at the offsets using the color_wheel effect
        for i, y_offset in enumerate(y_offsets):
            tft.draw.pixel(
                half + tween, (scroll + y_offset) % height, palette[wheel + (i << 2)]
            )
            tft.draw.pixel(
                half - tween, (scroll + y_offset) % height, palette[wheel + (i << 2)]
            )

        # increment scroll, counter, and wheel
        scroll = (scroll + 1) % height
        wheel = (wheel + 1) % 256
        counter += 1


main()
