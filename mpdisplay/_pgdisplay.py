# SPDX-FileCopyrightText: 2024 Brad Barnett
#
# SPDX-License-Identifier: MIT
"""
An implementation of an LCD library written in Python using pygame
"""

from . import _BaseDisplay, Events
import pygame as pg


class PGDisplay(_BaseDisplay):
    '''
    A class to emulate an LCD using pygame.
    Provides scrolling and rotation functions similar to an LCD.  The .texture
    object functions as the LCD's internal memory.
    '''

    def __init__(
        self,
        width=320,
        height=240,
        rotation=0,
        color_depth=16,
        title="MPDisplay",
        scale=None,
        window_flags=pg.SHOWN,
    ):
        """
        Initializes the sdl2lcd instance with the given parameters.

        :param width: The width of the display (default is 320).
        :type width: int
        :param height: The height of the display (default is 240).
        :type height: int
        :param rotation: The rotation of the display (default is 0).
        :type rotation: int
        :param color_depth: The color depth of the display (default is 16).
        :type color_depth: int
        :param title: The title of the display window (default is "MicroPython").
        :type title: str
        :param scale: The scale of the display (default is None).
        :type scale: float
        :param window_flags: The flags for creating the display window (default is pg.SHOWN).
        :type window_flags: int
        """
        print("MPDisplay: Using pygame display.")
        super().__init__()
        self._width = width
        self._height = height
        self._rotation = rotation
        self.color_depth = color_depth
        self._title = title
        self._window_flags = window_flags
        self._scale = scale if scale else 1
        self.requires_byte_swap = False
        self._buffer = None

        if scale is not None and scale != 1:
            print("Scaling is not implemented in PGDisplay.  Ignoring.")
        self._bytes_per_pixel = color_depth // 8

        pg.init()

        self.init()

    def init(self):
        """
        Initializes the sdl2lcd instance.  Called by __init__ and rotation setter.
        """
        self._display = pg.display.set_mode(size=(int(self.width), int(self.height)), flags=self._window_flags, depth=self.color_depth, display=0, vsync=0)
        pg.display.set_caption(self._title)

        self._buffer = pg.Surface(size=self._display.get_size(), depth=self.color_depth)
        self._buffer.fill((0, 0, 0))
        
        super().vscrdef(0, self.height, 0)  # Set the vertical scroll definition without calling _show
        self.vscsad(False)  # Scroll offset; set to False to disable scrolling

    def blit(self, x, y, w, h, buffer):
        """
        Blits a buffer to the display.
        
        :param x: The x-coordinate of the display.
        :type x: int
        :param y: The y-coordinate of the display.
        :type y: int
        :param w: The width of the display.
        :type w: int
        :param h: The height of the display.
        :type h: int
        :param buffer: The buffer to blit to the display.
        :type buffer: bytearray
        """

        blitRect = pg.Rect(x, y, w, h)
        for i in range(h):
            for j in range(w):
                pixel_index = (i * w + j) * self._bytes_per_pixel
                color = self._colorRGB(buffer[pixel_index:pixel_index + self._bytes_per_pixel])
                self._buffer.set_at((x + j, y + i), color)
        self._show(blitRect)

    def fill_rect(self, x, y, w, h, color):
        """
        Fill a rectangle with a color.

        Renders to the texture instead of directly to the window
        to facilitate scrolling and scaling.

        :param x: The x-coordinate of the rectangle.
        :type x: int
        :param y: The y-coordinate of the rectangle.
        :type y: int
        :param w: The width of the rectangle.
        :type w: int
        :param h: The height of the rectangle.
        :type h: int
        :param color: The color of the rectangle.
        :type color: int
        """
        fillRect = pg.Rect(x, y, w, h)
        self._buffer.fill(self._colorRGB(color), fillRect)
        self._show(fillRect)

    def vscrdef(self, tfa, vsa, bfa):
        """
        Set the vertical scroll definition.

        :param tfa: The top fixed area.
        :type tfa: int
        :param vsa: The vertical scroll area.
        :type vsa: int
        :param bfa: The bottom fixed area.
        :type bfa: int
        """
        super().vscrdef(tfa, vsa, bfa)
        self._show()

    def vscsad(self, y=None):
        """
        Set the vertical scroll start address.
        
        :param y: The vertical scroll start address.
        :type y: int
        """
        ret = super().vscsad(y)
        if y is not None:
            self._show()
        else:
            return ret

    def deinit(self):
        """
        Deinitializes the pygame instance.
        """
        pg.quit()

    def _show(self, renderRect=None):
        """
        Show the display.  Automatically called after blitting or filling the display.

        :param renderRect: The rectangle to render (default is None).
        :type renderRect: pg.Rect
        """
        if (y_start := self.vscsad()) == False:
            renderRect = pg.Rect(0, 0, self.width, self.height) if renderRect is None else renderRect
            self._display.blit(self._buffer, renderRect, renderRect)
        else:
            # Ignore renderRect and render the entire texture to the window in four steps
            if self._tfa > 0:
                tfaRect = pg.Rect(0, 0, self.width, self._tfa)
                self._display.blit(self._buffer, tfaRect, tfaRect)

            vsaTopHeight = self._vsa + self._tfa - y_start
            vsaTopSrcRect = pg.Rect(0, y_start, self.width, vsaTopHeight)
            vsaTopDestRect = pg.Rect(0, self._tfa, self.width, vsaTopHeight)
            self._display.blit(self._buffer, vsaTopDestRect, vsaTopSrcRect)

            vsaBtmHeight = self._vsa - vsaTopHeight
            vsaBtmSrcRect = pg.Rect(0, self._tfa, self.width, vsaBtmHeight)
            vsaBtmDestRect = pg.Rect(0, self._tfa + vsaTopHeight, self.width, vsaBtmHeight)
            self._display.blit(self._buffer, vsaBtmDestRect, vsaBtmSrcRect)

            if self._bfa > 0:
                bfaRect = pg.Rect(0, self._tfa + self._vsa, self.width, self._bfa)
                self._display.blit(self._buffer, bfaRect, bfaRect)

        pg.display.flip()

    def _colorRGB(self, color):
        if isinstance(color, int):
            # convert color from int to bytes
            if self.color_depth == 16:
                # convert 16-bit int color to 2 bytes
                color = [color & 0xFF, color >> 8]
            else:
                # convert 24-bit int color to 3 bytes
                color = [color & 0xFF, (color >> 8) & 0xFF, color >> 16]
        if len(color) == 2:
            r = color[1] & 0xF8 | (color[1] >> 5) & 0x7  # 5 bit to 8 bit red
            g = color[1] << 5 & 0xE0 | (color[0] >> 3) & 0x1F  # 6 bit to 8 bit green
            b = color[0] << 3 & 0xF8 | (color[0] >> 2) & 0x7  # 5 bit to 8 bit blue
        else:
            r, g, b = color
        return (r, g, b)


class PGEvents():
    """
    A class to poll events in pygame.
    """
    def read(self):
        """
        Polls for an event and returns the event type and data.

        :return: The event type and data.
        :rtype: tuple
        """
        if event := pg.event.poll():
            if event.type in Events.types:
                return event
        return None
