"""
feathers.py
===========

.. figure:: ../_static/feathers.jpg
    :align: center

    Test hardware scrolling.

Smoothly scrolls mirrored rainbow colored random curves across the display.

.. note:: This example requires the following modules:

  .. hlist::
    :columns: 3

    - `st7789py`
    - `tft_config`

"""

import random
import math
import time

import tft_config

palette = tft_config.palette


def between(left, right, along):
    """returns a point along the curve from left to right"""
    dist = (1 - math.cos(along * math.pi)) / 2
    return left * (1 - dist) + right * dist


def color_wheel(position):
    """returns a 565 color from the given position of the color wheel"""
    position = (255 - position) % 255

    if position < 85:
        return palette.color565(255 - position * 3, 0, position * 3)

    if position < 170:
        position -= 85
        return palette.color565(0, position * 3, 255 - position * 3)

    position -= 170
    return palette.color565(position * 3, 255 - position * 3, 0)


def main():
    """
    The big show!
    """
    # enable display and clear screen

    tft = tft_config.config(tft_config.FEATHERS)

    height = tft.height  # height of display in pixels
    width = tft.width  # width if display in pixels

    tfa = tft_config.TFA  # top free area when scrolling
    bfa = tft_config.BFA  # bottom free area when scrolling

    scroll = 0  # scroll position
    wheel = 0  # color wheel position

    tft.vscrdef(tfa, height, bfa)  # set scroll area
    tft.vscsad(scroll + tfa)  # set scroll position
    tft.draw.fill(palette.BLACK)  # clear screen

    half = (height >> 1) - 1  # half the height of the dislay
    interval = 0  # steps between new points
    increment = 0  # increment per step
    counter = 1  # step counter, overflow to start
    current_y = 0  # current_y value (right point)
    last_y = 0  # last_y value (left point)

    # segment offsets
    x_offsets = [x * (width // 8) - 1 for x in range(2, 9)]

    while True:
        # when the counter exceeds the interval, save current_y to last_y,
        # choose a new random value for current_y between 0 and 1/2 the
        # height of the display, choose a new random interval then reset
        # the counter to 0

        if counter > interval:
            last_y = current_y
            current_y = random.randint(0, half)
            counter = 0
            interval = random.randint(10, 100)
            increment = 1 / interval  # increment per step

        # clear the first column of the display and scroll it
        tft.draw.vline(scroll, 0, height, palette.BLACK)
        tft.vscsad(scroll + tfa)

        # get the next point between last_y and current_y
        tween = int(between(last_y, current_y, counter * increment))

        # draw mirrored pixels across the display at the offsets using the color_wheel effect
        for i, x_offset in enumerate(x_offsets):
            tft.draw.pixel(
                (scroll + x_offset) % width, half + tween, color_wheel(wheel + (i << 2))
            )
            tft.draw.pixel(
                (scroll + x_offset) % width, half - tween, color_wheel(wheel + (i << 2))
            )

        # increment scroll, counter, and wheel
        scroll = (scroll + 1) % width
        wheel = (wheel + 1) % 256
        counter += 1


main()
