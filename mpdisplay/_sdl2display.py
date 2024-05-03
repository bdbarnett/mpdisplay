# SPDX-FileCopyrightText: 2024 Brad Barnett
#
# SPDX-License-Identifier: MIT
"""
An implementation of an SDL2 Bus library written in MicroPython.
"""

from . import _BaseDisplay, Events
from sys import implementation
if implementation.name == 'cpython':
    is_cpython = True
    import ctypes
else:
    is_cpython = False

from sdl2_lib import (
    SDL_Init, SDL_Quit, SDL_GetError, SDL_CreateWindow, SDL_CreateRenderer, SDL_PollEvent,
    SDL_DestroyWindow, SDL_DestroyRenderer, SDL_DestroyTexture, SDL_SetRenderDrawColor,
    SDL_RenderClear, SDL_RenderPresent, SDL_RenderSetLogicalSize, SDL_SetWindowSize,
    SDL_SetRenderTarget, SDL_SetTextureBlendMode, SDL_RenderFillRect, SDL_RenderCopy,
    SDL_UpdateTexture, SDL_CreateTexture, SDL_GetKeyName, SDL_Rect, SDL_Event, SDL_QUIT,
    SDL_PIXELFORMAT_ARGB8888, SDL_PIXELFORMAT_RGB888, SDL_PIXELFORMAT_RGB565, SDL_TEXTUREACCESS_TARGET,
    SDL_BLENDMODE_NONE, SDL_RENDERER_ACCELERATED, SDL_RENDERER_PRESENTVSYNC, SDL_WINDOWPOS_CENTERED,
    SDL_WINDOW_SHOWN, SDL_INIT_EVERYTHING, SDL_BUTTON_LMASK, SDL_BUTTON_MMASK, SDL_BUTTON_RMASK,
    SDL_MOUSEBUTTONDOWN, SDL_MOUSEBUTTONUP, SDL_MOUSEMOTION, SDL_MOUSEWHEEL, SDL_KEYDOWN, SDL_KEYUP,
)

def retcheck(retvalue):
    # Check the return value of an SDL function and raise an exception if it's not 0
    if retvalue:
        raise RuntimeError(SDL_GetError())


class SDL2Display(_BaseDisplay):
    '''
    A class to create and manage the SDL2 window and renderer and emulate an LCD.
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
        x=SDL_WINDOWPOS_CENTERED,
        y=SDL_WINDOWPOS_CENTERED,
        title="SDL2 Display",
        window_flags=SDL_WINDOW_SHOWN,
        render_flags=SDL_RENDERER_ACCELERATED | SDL_RENDERER_PRESENTVSYNC,
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
        :param x: The x-coordinate of the display window's position (default is SDL_WINDOWPOS_CENTERED).
        :type x: int
        :param y: The y-coordinate of the display window's position (default is SDL_WINDOWPOS_CENTERED).
        :type y: int
        :param title: The title of the display window (default is "MicroPython").
        :type title: str
        :param window_flags: The flags for creating the display window (default is SDL_WINDOW_SHOWN).
        :type window_flags: int
        :param render_flags: The flags for creating the renderer (default is SDL_RENDERER_ACCELERATED | SDL_RENDERER_PRESENTVSYNC).
        :type render_flags: int
        """
        super().__init__()
        self._width = width
        self._height = height
        self._rotation = rotation
        self.color_depth = color_depth
        self._scale = scale
        self._tfa = self._bfa = 0  # Top and bottom fixed areas
        self._scroll_y = None  # Scroll offset; set to None to disable scrolling
        self.texture = None

        # Determine the pixel format
        if color_depth == 32:
            self._px_format = SDL_PIXELFORMAT_ARGB8888
        elif color_depth == 24:
            self._px_format = SDL_PIXELFORMAT_RGB888
        elif color_depth == 16:
            self._px_format = SDL_PIXELFORMAT_RGB565
        else:
            raise ValueError("Unsupported color_depth")
        
        retcheck(SDL_Init(SDL_INIT_EVERYTHING))
        self.win = SDL_CreateWindow(title.encode(), x, y, int(self.width*scale), int(self.height*scale), window_flags)
        if not self.win:
            raise RuntimeError(f"{SDL_GetError()}")

        self.renderer = SDL_CreateRenderer(self.win, -1, render_flags)
        if not self.renderer:
            raise RuntimeError(f"{SDL_GetError()}")

        self.requires_byte_swap = False

        self.init()

    def init(self):
        """
        Initializes the sdl2lcd instance.
        """
        self._vsa = self.height - self._tfa - self._bfa  # Vertical scaling area
        retcheck(SDL_RenderSetLogicalSize(self.renderer, self.width, self.height))
        retcheck(SDL_SetRenderDrawColor(self.renderer, 0, 0, 0, 255))
        retcheck(SDL_RenderClear(self.renderer))
        retcheck(SDL_RenderPresent(self.renderer))

        self.texture = SDL_CreateTexture(
            self.renderer, self._px_format, SDL_TEXTUREACCESS_TARGET, self.width, self.height)
        if not self.texture:
            raise RuntimeError(f"{SDL_GetError()}")
        retcheck(SDL_SetTextureBlendMode(self.texture, SDL_BLENDMODE_NONE))

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

        retcheck(SDL_SetWindowSize(self.win, int(self.width*self._scale), int(self.height*self._scale)))
        retcheck(SDL_DestroyTexture(self.texture))
        self.init()

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
        pitch = int(w * self.color_depth // 8)
        if len(buffer) != pitch * h:
            raise ValueError("Buffer size does not match dimensions")
        blitRect = SDL_Rect(x, y, w, h)
        if is_cpython:
            if type(buffer) is memoryview:
                buffer_array = (ctypes.c_ubyte * len(buffer.obj)).from_buffer(buffer.obj)
            else:
                buffer_array = (ctypes.c_ubyte * len(buffer)).from_buffer(buffer)
            buffer_ptr = ctypes.c_void_p(ctypes.addressof(buffer_array))
            retcheck(SDL_UpdateTexture(self.texture, blitRect, buffer_ptr, pitch))
        else:
            retcheck(SDL_UpdateTexture(self.texture, blitRect, buffer, pitch))
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
        fillRect = SDL_Rect(x, y, w, h)
        if self.color_depth == 16:
            r = (color >> 8) & 0xF8 | (color >> 13) & 0x7  # 5 bit to 8 bit red
            g = (color >> 3) & 0xFC | (color >> 9) & 0x3  # 6 bit to 8 bit green
            b = (color << 3) & 0xF8 | (color >> 2) & 0x7  # 5 bit to 8 bit blue
        else:
            r, g, b = color >> 16 & 0xFF, (color >> 8) & 0xFF, color & 0xFF

        retcheck(SDL_SetRenderTarget(self.renderer, self.texture))  # Set the render target to the texture
        retcheck(SDL_SetRenderDrawColor(self.renderer, r, g, b, 255))  # Set the color to fill the rectangle
        retcheck(SDL_RenderFillRect(self.renderer, fillRect))  # Fill the rectangle on the texture
        retcheck(SDL_SetRenderTarget(self.renderer, None))  # Reset the render target back to the window
        self._show(fillRect)

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

    def vscsad(self, y):
        """
        Set the vertical scroll start address.
        
        :param y: The vertical scroll start address.
        :type y: int
        """
        self._scroll_y = y
        self._show()

    def deinit(self):
        """
        Deinitializes the sdl2lcd instance.
        """
        retcheck(SDL_DestroyTexture(self.texture))
        retcheck(SDL_DestroyRenderer(self.renderer))
        retcheck(SDL_DestroyWindow(self.win))
        retcheck(SDL_Quit())

    def _show(self, renderRect=None):
        """
        Show the display.  Automatically called after blitting or filling the display.

        :param renderRect: The rectangle to render (default is None).
        :type renderRect: SDL_Rect
        """
        if self._scroll_y == None:
            retcheck(SDL_RenderCopy(self.renderer, self.texture, renderRect, renderRect))
        else:
            # Ignore renderRect and render the entire texture to the window in four steps
            if self._tfa > 0:
                tfaRect = SDL_Rect(0, 0, self.width, self._tfa)
                retcheck(SDL_RenderCopy(self.renderer, self.texture, tfaRect, tfaRect))

            vsaTopHeight = self._vsa + self._tfa - self._scroll_y
            vsaTopSrcRect = SDL_Rect(0, self._scroll_y, self.width, vsaTopHeight)
            vsaTopDestRect = SDL_Rect(0, self._tfa, self.width, vsaTopHeight)
            retcheck(SDL_RenderCopy(self.renderer, self.texture, vsaTopSrcRect, vsaTopDestRect))

            vsaBtmHeight = self._vsa - vsaTopHeight
            vsaBtmSrcRect = SDL_Rect(0, self._tfa, self.width, vsaBtmHeight)
            vsaBtmDestRect = SDL_Rect(0, self._tfa + vsaTopHeight, self.width, vsaBtmHeight)
            retcheck(SDL_RenderCopy(self.renderer, self.texture, vsaBtmSrcRect, vsaBtmDestRect))

            if self._bfa > 0:
                bfaRect = SDL_Rect(0, self._tfa + self._vsa, self.width, self._bfa)
                retcheck(SDL_RenderCopy(self.renderer, self.texture, bfaRect, bfaRect))

        retcheck(SDL_RenderPresent(self.renderer))


class SDL2Events():
    """
    An implementation of an SDL2 event poller.
    """
    def __init__(self):
        """
        Initializes the SDL2Events instance.
        """
        super().__init__()
        self._event = SDL_Event()

    def read(self):
        """
        Polls for an event and returns the event type and data.

        :return: The event type and data.
        :rtype: tuple
        """
        if SDL_PollEvent(self._event):
            if is_cpython:
                if self._event.type in Events.types:
                    return self._convert(SDL_Event(self._event))
            else:
                if int.from_bytes(self._event[:4], 'little') in Events.types:
                    return self._convert(SDL_Event(self._event))
        return None

    @staticmethod
    def _convert(e):
        if e.type == SDL_MOUSEMOTION:
            l = 1 if e.motion.state & SDL_BUTTON_LMASK else 0
            m = 1 if e.motion.state & SDL_BUTTON_MMASK else 0
            r = 1 if e.motion.state & SDL_BUTTON_RMASK else 0
            evt = Events.Motion(e.type, (e.motion.x, e.motion.y), (e.motion.xrel, e.motion.yrel), (l, m, r), e.motion.which != 0, e.motion.windowID)
        elif e.type in (SDL_MOUSEBUTTONDOWN, SDL_MOUSEBUTTONUP):
            evt = Events.Button(e.type, (e.button.x, e.button.y), e.button.button, e.button.which != 0, e.button.windowID)
        elif e.type == SDL_MOUSEWHEEL:
            evt = Events.Wheel(e.type, e.wheel.direction != 0, e.wheel.x, e.wheel.y, e.wheel.preciseX, e.wheel.preciseY, e.wheel.which != 0, e.wheel.windowID)
        elif e.type in (SDL_KEYDOWN, SDL_KEYUP):
            name = SDL_GetKeyName(e.key.keysym.sym)
            evt = Events.Key(e.type, name, e.key.keysym.sym, e.key.keysym.mod, e.key.keysym.scancode, e.key.windowID)
        elif e.type == SDL_QUIT:
            evt = Events.Quit(e.type)
        else:
            evt = Events.Unknown(e.type)
        return evt
