# SPDX-FileCopyrightText: 2024 Brad Barnett and Kevin Schlosser
#
# SPDX-License-Identifier: MIT

"""
_BaseDisplay class for all display drivers to inherit from.
"""

from . import Broker, Devices
from primitives import DisplayShapes, Area
from sys import exit  # default for self.quit


class _BaseDisplay(Broker, DisplayShapes):

    def __init__(self):
        super().__init__()
        self._vssa = False  # False means no vertical scroll
        self.requires_byte_swap = False

        # Function to call when the window close button is clicked.
        # Set it like `display_drv.quit_func = cleanup_func` where `cleanup_func` is a
        # function that cleans up resources and calls `sys.exit()`.
        # .poll() must be called periodically to check for the quit event.
        self.quit_func = exit

    ############### Common API Methods ################

    @property
    def width(self):
        """The width of the display in pixels."""
        if ((self._rotation // 90) & 0x1) == 0x1:  # if rotation index is odd
            return self._height
        return self._width

    @property
    def height(self):
        """The height of the display in pixels."""
        if ((self._rotation // 90) & 0x1) == 0x1:  # if rotation index is odd
            return self._width
        return self._height

    @property
    def rotation(self):
        """
        The rotation of the display.

        :return: The rotation of the display.
        :rtype: int
        """
        return self._rotation

    @rotation.setter
    def rotation(self, value):
        """
        Sets the rotation of the display.

        :param value: The rotation of the display.
        :type value: int
        """

        value = self._rotation_helper(value)

        if value == self._rotation:
            return

        self._rotation = value

        for device in self.devices:
            if device.type == Devices.TOUCH:
                device.rotation = value

        self.init()

    def _rotation_helper(self, value):
        """
        Helper function to set the rotation of the display.

        :param value: The rotation of the display.
        :type value: int
        """
        # if the value is not a multiple of 90, it is in quarter turns
        if value % 90 != 0:
            value = value * 90
        return value

    @property
    def quit_func(self):
        """
        The function to call when the window close button is clicked.
        """
        return self._quit_func

    @quit_func.setter
    def quit_func(self, value):
        """
        Sets the function to call when the window close button is clicked.

        :param value: The function to call.
        """
        if not callable(value):
            raise ValueError("quit_func must be callable")
        self._quit_func = value

    def quit(self):
        """
        Call the quit function.
        """
        self._quit_func()

    def fill(self, color):
        """
        Fill the display with a color.

        :param color: The color to fill the display with.
        :type color: int
        """
        self.fill_rect(0, 0, self.width, self.height, color)
        return Area(0, 0, self.width, self.height)

    def pixel(self, x, y, color):
        """
        Set a pixel on the display.

        :param x: The x-coordinate of the pixel.
        :type x: int
        :param y: The y-coordinate of the pixel.
        :type y: int
        :param color: The color of the pixel.
        :type color: int
        """
        self.blit_rect(bytearray(color.to_bytes(2, "little")), x, y, 1, 1)
        return Area(x, y, 1, 1)

    def scroll(self, dx, dy):
        """
        Scroll the display.

        :param dx: The x-coordinate to scroll.  Not supported.
        :type dx: int
        :param dy: The y-coordinate to scroll.
        :type dy: int
        """
        if dy != 0:
            if self._vssa is not None:
                self.vscsad(self._vssa + dy)
            else:
                self.vscsad(dy)
        if dx != 0:
            raise NotImplementedError("Horizontal scrolling not supported")

    def color888(self, r, g, b):
        """
        Convert RGB values to a 24-bit color value.

        :param r: The red value.
        :type r: int
        :param g: The green value.
        :type g: int
        :param b: The blue value.
        :type b: int
        :return: The 24-bit color value.
        :rtype: int
        """
        return (r << 16) | (g << 8) | b

    def color565(self, r, g=0, b=0):
        """
        Convert RGB values to a 16-bit color value.

        :param r: The red value.
        :type r: int
        :param g: The green value.
        :type g: int
        :param b: The blue value.
        :type b: int
        :return: The 16-bit color value.
        :rtype: int
        """
        if isinstance(r, (tuple, list)):
            r, g, b = r[:3]
        return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)

    def color565_swapped(self, r, g=0, b=0):
        # Convert r, g, b in range 0-255 to a 16 bit color value RGB565
        # ggbbbbbb rrrrrggg
        if isinstance(r, (tuple, list)):
            r, g, b = r[:3]
        color = self.color565(r, g, b)
        return (color & 0xFF) << 8 | (color & 0xFF00) >> 8

    def color_wheel(self, pos):
        """
        Get a color from the color wheel.

        :param pos: The position on the color wheel.
        :type pos: int
        :return: The color value.
        :rtype: int
        """
        pos = 255 - pos
        if pos < 85:
            return self.color565(255 - pos * 3, 0, pos * 3)
        if pos < 170:
            pos -= 85
            return self.color565(0, pos * 3, 255 - pos * 3)
        pos -= 170
        return self.color565(pos * 3, 255 - pos * 3, 0)

    def color332(self, r, g, b):
        # Convert r, g, b in range 0-255 to an 8 bit color value RGB332
        # rrrgggbb
        return (r & 0xE0) | ((g >> 3) & 0x1C) | (b >> 6)

    def color_rgb(self, color):
        if isinstance(color, int):
            # convert color from int to bytes
            if self.color_depth == 16:
                # convert 16-bit int color to 2 bytes
                color = (color & 0xFF, color >> 8)
            else:
                # convert 24-bit int color to 3 bytes
                color = (color & 0xFF, (color >> 8) & 0xFF, color >> 16)
        if len(color) == 2:
            r = color[1] & 0xF8 | (color[1] >> 5) & 0x7  # 5 bit to 8 bit red
            g = color[1] << 5 & 0xE0 | (color[0] >> 3) & 0x1F  # 6 bit to 8 bit green
            b = color[0] << 3 & 0xF8 | (color[0] >> 2) & 0x7  # 5 bit to 8 bit blue
        else:
            r, g, b = color
        return (r, g, b)

    def __del__(self):
        """
        Deinitializes the display instance.
        """
        self.deinit()

    ############### Overriden API Methods ################
    def blit_rect(self, buffer, x, y, width, height):
        # should be overridden and called upon completion as
        # super().blit_rect(buffer, x, y, width, height)
        """
        Blit a buffer to the display.

        :param buffer: The buffer to blit to the display.
        :type buffer: bytearray
        :param x: The x-coordinate of the display.
        :type x: int
        :param y: The y-coordinate of the display.
        :type y: int
        :param width: The width of the display.
        :type width: int
        :param height: The height of the display.
        :type height: int
        """
        return Area(x, y, width, height)

    def fill_rect(self, x, y, width, height, color):
        # should be overridden and called upon completion as
        # super().fill_rect(x, y, width, height, color)
        """
        Fill a rectangle on the display with a color.

        :param x: The x-coordinate of the rectangle.
        :type x: int
        :param y: The y-coordinate of the rectangle.
        :type y: int
        :param width: The width of the rectangle.
        :type width: int
        :param height: The height of the rectangle.
        :type height: int
        :param color: The color to fill the rectangle with.
        :type color: int
        """
        return Area(x, y, width, height)

    def vscrdef(self, tfa, vsa, bfa):
        """
        Set the vertical scroll definition.  Should be overridden by the
        subclass and called as super().vscrdef(tfa, vsa, bfa).

        :param tfa: The top fixed area.
        :type tfa: int
        :param vsa: The vertical scrolling area.
        :type vsa: int
        :param bfa: The bottom fixed area.
        :type bfa: int
        """
        if tfa + vsa + bfa != self.height:
            raise ValueError(
                "Sum of top, scroll and bottom areas must equal screen height"
            )
        self._tfa = tfa
        self._vsa = vsa
        self._bfa = bfa

    def vscsad(self, vssa=None):
        """
        Set the vertical scroll start address.  Should be overridden by the
        subclass and called as super().vscsad(y).

        :param y: The vertical scroll start address.
        :type y: int
        """
        if vssa is not None:
            self._vssa = vssa
        else:
            return self._vssa

    def set_render_mode_full(self, render_mode_full=False):
        return

    @property
    def power(self):
        return -1

    @power.setter
    def power(self, value):
        return

    @property
    def brightness(self):
        return -1

    @brightness.setter
    def brightness(self, value):
        return

    def invert_colors(self, value):
        return

    def reset(self):
        return

    def hard_reset(self):
        return

    def soft_reset(self):
        return

    def sleep_mode(self, value):
        return
