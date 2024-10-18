# SPDX-FileCopyrightText: 2024 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""
PyDevices basedisplay
"""

import gc
from sys import implementation
from ._area import Area
from ._color import color_rgb, color565, color565_swapped, color332, color888  # noqa: F401

try:
    from typing import Optional
except ImportError:
    pass

np = False
try:
    import ulab.numpy as np  # type: ignore
except ImportError:
    try:
        import numpy as np  # type: ignore
    except ImportError:
        pass

viper = False
if implementation.name == "micropython":
    try:
        from ._viper import swap_bytes

        viper = True
    except Exception as e:
        print(f"PyDevices:  {e}")

if not viper:
    if np:
        from ._numpy import swap_bytes
    else:

        def swap_bytes(buf, buf_size_pix):
            buf[::2], buf[1::2] = buf[1::2], buf[::2]


gc.collect()


class DisplayDriver:
    def __init__(self):
        gc.collect()
        self._vssa = False  # False means no vertical scroll
        self._requires_byte_swap = False
        self._auto_byte_swap_enabled = self._requires_byte_swap
        self._touch_device = None
        print(f"{self.__class__.__name__} initialized.")
        gc.collect()

    def __del__(self):
        self.deinit()

    ############### Universal API Methods, not usually overridden ################

    @property
    def width(self) -> int:
        """The width of the display in pixels."""
        if ((self._rotation // 90) & 0x1) == 0x1:  # if rotation index is odd
            return self._height
        return self._width

    @property
    def height(self) -> int:
        """The height of the display in pixels."""
        if ((self._rotation // 90) & 0x1) == 0x1:  # if rotation index is odd
            return self._width
        return self._height

    @property
    def rotation(self) -> int:
        """
        The rotation of the display.
        """
        return self._rotation

    @rotation.setter
    def rotation(self, value) -> None:
        """
        Sets the rotation of the display.

        Args:
            value (int): The rotation of the display in degrees.
        """

        if value % 90 != 0:
            value = value * 90

        if value == self._rotation:
            return

        print(f"{self.__class__.__name__}.rotation():  Setting rotation to {value}")
        self._rotation_helper(value)

        self._rotation = value

        if self._touch_device is not None:
            self._touch_device.rotation = value

        self.init()

    @property
    def touch_device(self) -> object:
        """
        The touch device.
        """
        return self._touch_device

    @touch_device.setter
    def touch_device(self, value) -> None:
        """
        Sets the touch device.

        Args:
            value (object): The touch device.
        """
        if hasattr(value, "rotation") or value is None:
            self._touch_device = value
        else:
            raise ValueError("touch_device must have a rotation attribute")
        self._touch_device.rotation = self.rotation

    def fill(self, color) -> Area:
        """
        Fill the display with a color.

        Args:
            color (int): The color to fill the display with.

        Returns:
            Area: The area that was filled.
        """
        self.fill_rect(0, 0, self.width, self.height, color)
        return Area(0, 0, self.width, self.height)

    def scroll(self, dx, dy) -> None:
        """
        Scroll the display.

        Args:
            dx (int): The number of pixels to scroll horizontally.
            dy (int): The number of pixels to scroll vertically.
        """
        if dy != 0:
            if self._vssa is not None:
                self.vscsad(self._vssa + dy)
            else:
                self.vscsad(dy)
        if dx != 0:
            raise NotImplementedError("Horizontal scrolling not supported")

    def disable_auto_byte_swap(self, value: bool) -> bool:
        """
        Disable byte swapping in the display driver.

        If self.requires_byte_swap and the guest application is capable of byte swapping color data
        check to see if byte swapping can be disabled.  If so, disable it.

        Usage:
            ```
            # If byte swapping is required and the display driver is capable of having byte swapping disabled,
            # disable it and set a flag so we can swap the color bytes as they are created.
            if display_drv.requires_byte_swap:
                needs_swap = display_drv.disable_auto_byte_swap(True)
            else:
                needs_swap = False
            ```

        Args:
            value (bool): Whether to disable byte swapping.

        Returns:
            bool: Whether byte swapping was disabled successfully.

        """
        if self._requires_byte_swap:
            self._auto_byte_swap_enabled = not value
        else:
            self._auto_byte_swap_enabled = False
        print(
            f"{self.__class__.__name__}:  auto byte swapping = {self._auto_byte_swap_enabled}"
        )
        return not self._auto_byte_swap_enabled

    @property
    def requires_byte_swap(self) -> bool:
        """
        Whether the display requires byte swapping.
        """
        return self._requires_byte_swap

    def blit_transparent(
        self, buf: memoryview, x: int, y: int, w: int, h: int, key: int
    ) -> Area:
        """
        Blit a buffer with transparency.

        Args:
            buf (memoryview): The buffer to blit.
            x (int): The x coordinate to blit to.
            y (int): The y coordinate to blit to.
            w (int): The width to blit.
            h (int): The height to blit.
            key (int): The color key to use for transparency.

        Returns:
            Area: The area that was blitted.
        """
        BPP = self.color_depth // 8
        key_bytes = key.to_bytes(BPP, "little")
        stride = w * BPP
        for j in range(h):
            rowstart = j * stride
            colstart = 0
            # iterate over each pixel looking for the first non-key pixel
            while colstart < stride:
                startoffset = rowstart + colstart
                if buf[startoffset : startoffset + BPP] != key_bytes:
                    # found a non-key pixel
                    # then iterate over each pixel looking for the next key pixel
                    colend = colstart
                    while colend < stride:
                        endoffset = rowstart + colend
                        if buf[endoffset : endoffset + BPP] == key_bytes:
                            break
                        colend += BPP
                    # blit the non-key pixels
                    self.blit_rect(
                        buf[rowstart + colstart : rowstart + colend],
                        x + colstart // BPP,
                        y + j,
                        (colend - colstart) // BPP,
                        1,
                    )
                    colstart = colend
                else:
                    colstart += BPP
        return Area(x, y, w, h)

    @property
    def vscroll(self) -> int:
        """
        The vertical scroll position relative to the top fixed area.

        Returns:
            int: The vertical scroll position.
        """
        return self.vscsad() - self._tfa

    @vscroll.setter
    def vscroll(self, y) -> None:
        """
        Set the vertical scroll position relative to the top fixed area.

        Args:
            y (int): The vertical scroll position.
        """
        self.vscsad((y % self._vsa) + self._tfa)

    def set_vscroll(self, tfa=0, bfa=0) -> None:
        """
        Set the vertical scroll definition and move the vertical scroll to the top.

        Args:
            tfa (int): The top fixed area.
            bfa (int): The bottom fixed area.
        """
        self.vscrdef(tfa, self.height - tfa - bfa, bfa)
        self.vscroll = 0

    @property
    def tfa(self) -> int:
        """
        The top fixed area set by set_vscroll or vscrdef.

        Returns:
            int: The top fixed area.
        """
        return self._tfa
    
    @property
    def vsa(self) -> int:
        """
        The vertical scroll area set by set_vscroll or vscrdef.

        Returns:
            int: The vertical scroll area.
        """
        return self._vsa
    
    @property
    def bfa(self) -> int:
        """
        The bottom fixed area set by set_vscroll or vscrdef.

        Returns:
            int: The bottom fixed area.
        """
        return self._bfa

    def translate_point(self, point) -> tuple:
        """
        Translate a point from real coordinates to scrolled coordinates.

        Useful for touch events.

        Args:
            point (tuple): The x and y coordinates to translate.

        Returns:
            tuple: The translated x and y coordinates.
        """
        x, y = point
        if self.vscsad() and self.tfa < y < self.height - self.bfa:
            y = y + self.vscsad() - self.tfa
            if y >= (self.vsa + self.tfa):
                y %= self.vsa
        return x, y

    def scroll_by(self, value):
        self.vscroll += value

    def scroll_to(self, value):
        self.vscroll = value

    @property
    def tfa_area(self) -> Area:
        """
        The top fixed area as an Area object.

        Returns:
            Area: The top fixed area.
        """
        return Area(0, 0, self.width, self.tfa)
    
    @property
    def vsa_area(self) -> Area:
        """
        The vertical scroll area as an Area object.

        Returns:
            Area: The vertical scroll area.
        """
        return Area(0, self.tfa, self.width, self.vsa)
    
    @property
    def bfa_area(self) -> Area:
        """
        The bottom fixed area as an Area object.

        Returns:
            Area: The bottom fixed area.
        """
        return Area(0, self.tfa + self.vsa, self.width, self.bfa)
    

    ############### Common API Methods, sometimes overridden ################

    def vscrdef(self, tfa: int, vsa: int, bfa: int) -> None:
        """
        Set the vertical scroll definition.  Should be overridden by the
        subclass and called as super().vscrdef(tfa, vsa, bfa).

        Args:
            tfa (int): The top fixed area.
            vsa (int): The vertical scroll area.
            bfa (int): The bottom fixed area.
        """
        if tfa + vsa + bfa != self.height:
            raise ValueError(
                "Sum of top, scroll and bottom areas must equal screen height"
            )
        self._tfa = tfa
        self._vsa = vsa
        self._bfa = bfa

    def vscsad(self, vssa: Optional[int] = None) -> int:
        """
        Set or get the vertical scroll start address.  Should be overridden by the
        subclass and called as super().vscsad(y).

        Args:
            vssa (int): The vertical scroll start address.

        Returns:
            int: The vertical scroll start address.
        """
        if vssa is not None:
            while vssa < 0:
                vssa += self._height
            if vssa >= self._height:
                vssa %= self._height
            self._vssa = vssa
        return vssa

    def _rotation_helper(self, value):
        """
        Helper function to set the rotation of the display.

        :param value: The rotation of the display.
        :type value: int
        """
        # override this method in subclasses to handle rotation
        pass

    ############### Empty API Methods, must be overridden if applicable ################

    @property
    def power(self) -> bool:
        """The power state of the display."""
        return -1

    @power.setter
    def power(self, value: bool) -> None:
        """
        Set the power state of the display.  Should be overridden by the subclass.

        Args:
            value (bool): True to power on, False to power off.
        """
        return

    @property
    def brightness(self) -> float:
        """The brightness of the display."""
        return -1

    @brightness.setter
    def brightness(self, value: float) -> None:
        """
        Set the brightness of the display.  Should be overridden by the subclass.

        Args:
            value (int, float): The brightness value from 0 to 1.
        """
        return

    def invert_colors(self, value: bool) -> None:
        """
        Invert the colors of the display.  Should be overridden by the subclass.

        Args:
            value (bool): True to invert the colors, False to restore the colors.
        """
        return

    def reset(self) -> None:
        """
        Perform a reset of the display.  Should be overridden by the subclass.
        """
        return

    def hard_reset(self) -> None:
        """
        Perform a hardware reset of the display.  Should be overridden by the subclass.
        """
        return

    def soft_reset(self) -> None:
        """
        Perform a software reset of the display.  Should be overridden by the subclass.
        """
        return

    def sleep_mode(self, value: bool) -> None:
        """
        Set the sleep mode of the display.  Should be overridden by the subclass.

        Args:
            value (bool): True to enter sleep mode, False to exit sleep mode.
        """
        return

    def deinit(self) -> None:
        """
        Deinitialize the display.
        """
        self.__del__()
        return

    def show(self, *args, **kwargs) -> None:
        """
        Show the display.  Base class method does nothing.  May be overridden by subclasses.
        """
        return
