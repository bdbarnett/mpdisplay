# SPDX-FileCopyrightText: 2024 Brad Barnett
#
# SPDX-License-Identifier: MIT
from ._devices import Devices, DeviceController, Events
from sys import exit  # default for self.quit


class _BaseDisplay(DeviceController):

    def __init__(self):
        self._vssa = False  # False means no vertical scroll
        self.requires_byte_swap = False

        # Function to call when the window close button is clicked.
        # Set it like `display_drv.quit_func = cleanup_func` where `cleanup_func` is a
        # function that cleans up resources and calls `sys.exit()`.
        # .poll_event() must be called periodically to check for the quit event.
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
        if value == self._rotation:
            return

        self._rotation = value

        for device in self.devices:
            if device.type == Devices.TOUCH:
                device.rotation = value

        self.init()

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

    def __del__(self):
        """
        Deinitializes the display instance.
        """
        self.deinit()

    ############### Overriden API Methods ################

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
            raise ValueError("Sum of top, scroll and bottom areas must equal screen height")
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

    def reset(self):
        return

    def hard_reset(self):
        return

    def soft_reset(self):
        return

    def sleep_mode(self, value):
        return
