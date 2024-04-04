# SPDX-FileCopyrightText: 2024 Brad Barnett
#
# SPDX-License-Identifier: MIT
"""
An implementation of an LCD library written in Python using pygame
"""

import pygame as pg


class PGDisplay:
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
        scale=1,
        title="MPDisplay",
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
        :param scale: The scale factor for the display (default is 1).
        :type scale: int
        :param title: The title of the display window (default is "MicroPython").
        :type title: str
        :param window_flags: The flags for creating the display window (default is SDL_WINDOW_SHOWN).
        :type window_flags: int
        """
        self._width = width
        self._height = height
        self._rotation = rotation
        self.color_depth = color_depth
        self._scale = scale
        self._title = title
        self._window_flags = window_flags
        self._tfa = self._bfa = 0  # Top and bottom fixed areas
        self._scroll_y = None  # Scroll offset; set to None to disable scrolling
        self._bytes_per_pixel = color_depth // 8

        # Function to call when the window close button is clicked.
        # Set it like `display_drv.quit_func = cleanup_func` where `cleanup_func` is a 
        # function that cleans up resources and calls `sys.exit()`.
        # .poll_event() must be called periodically to check for the quit event.
        self.quit_func = lambda: print(".quit_func not set")

        self.requires_byte_swap = False

        pg.init()

        self._init()

    def _init(self):
        """
        Initializes the sdl2lcd instance.
        """
        self._vsa = self.height - self._tfa - self._bfa  # Vertical scaling area
        self.screen = pg.display.set_mode(size=(int(self.width*self._scale), int(self.height*self._scale)), flags=self._window_flags, depth=self.color_depth, display=0, vsync=0)
        pg.display.set_caption(self._title)
        self.screen.fill((255, 0, 0))
        pg.display.flip()

        self.frame_buffer = pg.Surface(size=self.screen.get_size(), depth=self.color_depth)
        self.frame_buffer.fill((0, 0, 0))

    @property
    def width(self):
        """
        The width of the display.
        
        :return: The width of the display.
        :rtype: int
        """
        if ((self._rotation // 90) & 1) == 1:  # if rotation index is odd
            return self._height
        return self._width

    @property
    def height(self):
        """
        The height of the display.
        
        :return: The height of the display.
        :rtype: int
        """
        if ((self._rotation // 90) & 1) == 1:  # if rotation index is odd
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

        self._init()

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
                self.frame_buffer.set_at((x + j, y + i), color)
        self._show(blitRect)

    def _colorRGB(self, color):
        if len(color) == 2:
            r = color[1] & 0xF8 | (color[1] >> 5) & 0x7  # 5 bit to 8 bit red
            g = color[1] << 5 & 0xE0 | (color[0] >> 3) & 0x1F  # 6 bit to 8 bit green
            b = color[0] << 3 & 0xF8 | (color[0] >> 2) & 0x7  # 5 bit to 8 bit blue
        else:
            r, g, b = color
        return (r, g, b)

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
        if self.color_depth == 16:
            r = (color >> 8) & 0xF8 | (color >> 13) & 0x7  # 5 bit to 8 bit red
            g = (color >> 3) & 0xFC | (color >> 9) & 0x3  # 6 bit to 8 bit green
            b = (color << 3) & 0xF8 | (color >> 2) & 0x7  # 5 bit to 8 bit blue
        else:
            r, g, b = color >> 16 & 0xFF, (color >> 8) & 0xFF, color & 0xFF

        self.frame_buffer.fill((r, g, b), fillRect)
        self._show(fillRect)

    def _show(self, renderRect=None):
        """
        Show the display.  Automatically called after blitting or filling the display.

        :param renderRect: The rectangle to render (default is None).
        :type renderRect: SDL_Rect
        """
        if self._scroll_y == None:
            renderRect = pg.Rect(0, 0, self.width, self.height) if renderRect is None else renderRect
            self.screen.blit(self.frame_buffer, renderRect, renderRect)
        else:
            # Ignore renderRect and render the entire texture to the window in four steps
            if self._tfa > 0:
                tfaRect = pg.Rect(0, 0, self.width, self._tfa)
                self.screen.blit(self.frame_buffer, tfaRect, tfaRect)

            vsaTopHeight = self._vsa + self._tfa - self._scroll_y
            vsaTopSrcRect = pg.Rect(0, self._scroll_y, self.width, vsaTopHeight)
            vsaTopDestRect = pg.Rect(0, self._tfa, self.width, vsaTopHeight)
            self.screen.blit(self.frame_buffer, vsaTopDestRect, vsaTopSrcRect)

            vsaBtmHeight = self._vsa - vsaTopHeight
            vsaBtmSrcRect = pg.Rect(0, self._tfa, self.width, vsaBtmHeight)
            vsaBtmDestRect = pg.Rect(0, self._tfa + vsaTopHeight, self.width, vsaBtmHeight)
            self.screen.blit(self.frame_buffer, vsaBtmDestRect, vsaBtmSrcRect)

            if self._bfa > 0:
                bfaRect = pg.Rect(0, self._tfa + self._vsa, self.width, self._bfa)
                self.screen.blit(self.frame_buffer, bfaRect, bfaRect)

        pg.display.flip()

    def vscsad(self, y):
        """
        Set the vertical scroll start address.
        
        :param y: The vertical scroll start address.
        :type y: int
        """
        self._scroll_y = y
        self._show()

    def vscrdef(self, tfa, vsa, bfa):
        """
        Set the vertical scroll definition.

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
        self._show()

    def poll_event(self):
        """
        Polls for an event and returns the event type and data.

        :return: The event type and data.
        :rtype: tuple
        """
        event = pg.event.poll()
        if event.type in (
            pg.QUIT,
            pg.KEYDOWN,
            pg.KEYUP,
            pg.MOUSEMOTION,
            pg.MOUSEBUTTONDOWN,
            pg.MOUSEBUTTONUP,
            pg.MOUSEWHEEL,
            ):
            if event.type == pg.QUIT:
                self.quit_func()
            elif event.type == pg.KEYDOWN or event.type == pg.KEYUP:
                return (event.type, event.unicode, event.mod)
            elif event.type == pg.MOUSEMOTION:
                return (
                    event.type,
                    event.pos[0],
                    event.pos[1],
                    event.rel[0],
                    event.rel[1],
                    event.buttons,
                )
            elif event.type == pg.MOUSEBUTTONDOWN or event.type == pg.MOUSEBUTTONUP:
                return (
                    event.type,
                    event.pos[0],
                    event.pos[1],
                    event.button,
                )
            elif event.type == pg.MOUSEWHEEL:
                return (event.type, event.x, event.y, event.flipped)
            else:  # Should never reach this point; left in so `if event_type in(...)` can be changed to `if True:` for debugging
                return event.type
        return None

    def get_touched(self):
        """
        Get the touch position from the SDL2 event queue.  If the event is
        SDL_MOUSEBUTTONDOWN and the left button is pressed, return the
        mouse position.  Otherwise, return None.
        
        :return: (x, y) tuple of the mouse position or None
        :rtype: tuple or None
        """
        # NOTE: This discards all events except MOUSEBUTTONDOWN on the left button
        event = self.poll_event()
        if event:
            # if the event is SDL_MOUSEBUTTONDOWN, return the mouse position
            if event[0] == pg.MOUSEBUTTONDOWN and event[3] == 1:
                return (event[1], event[2])
        return None

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

    def init(self, render_mode_full=False):
        return

    def set_render_mode_full(self, render_mode_full=False):
        return

    def deinit(self):
        """
        Deinitializes the pygame instance.
        """
        pg.quit()

    def __del__(self):
        """
        Deinitializes the pygame instance.
        """
        self.deinit()
