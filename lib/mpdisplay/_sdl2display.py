# SPDX-FileCopyrightText: 2024 Brad Barnett
#
# SPDX-License-Identifier: MIT
"""
An implementation of an SDL2 Bus library written in MicroPython.
"""

import uctypes
import ffi
import struct
from micropython import const
from . import _BaseDisplay, Events

###############################################################################
#                          SDL2 Constants                                     #
###############################################################################

# NOTE:  SDL_PIXELFORMAT_* values are at the end of this file, below the classes

# SDL_WindowPos values
SDL_WINDOWPOS_UNDEFINED = const(0x1FFF0000)
SDL_WINDOWPOS_CENTERED = const(0x2FFF0000)

# SDL_Window flags
SDL_WINDOW_FULLSCREEN = const(0x00000001)
SDL_WINDOW_OPENGL = const(0x00000002)
SDL_WINDOW_SHOWN = const(0x00000004)
SDL_WINDOW_HIDDEN = const(0x00000008)
SDL_WINDOW_BORDERLESS = const(0x00000010)
SDL_WINDOW_RESIZABLE = const(0x00000020)
SDL_WINDOW_MINIMIZED = const(0x00000040)
SDL_WINDOW_MAXIMIZED = const(0x00000080)
SDL_WINDOW_INPUT_GRABBED = const(0x00000100)
SDL_WINDOW_INPUT_FOCUS = const(0x00000200)
SDL_WINDOW_MOUSE_FOCUS = const(0x00000400)
SDL_WINDOW_FULLSCREEN_DESKTOP = const(0x00001001)
SDL_WINDOW_ALLOW_HIGHDPI = const(0x00002000)
SDL_WINDOW_MOUSE_CAPTURE = const(0x00004000)
SDL_WINDOW_ALWAYS_ON_TOP = const(0x00008000)
SDL_WINDOW_SKIP_TASKBAR = const(0x00010000)
SDL_WINDOW_UTILITY = const(0x00020000)
SDL_WINDOW_TOOLTIP = const(0x00040000)
SDL_WINDOW_POPUP_MENU = const(0x00080000)
SDL_WINDOW_VULKAN = const(0x10000000)

# SDL_Renderer flags
SDL_RENDERER_SOFTWARE = const(0x00000001)
SDL_RENDERER_ACCELERATED = const(0x00000002)
SDL_RENDERER_PRESENTVSYNC = const(0x00000004)
SDL_RENDERER_TARGETTEXTURE = const(0x00000008)

# SDL_Init flags
SDL_INIT_TIMER = const(0x00000001)
SDL_INIT_AUDIO = const(0x00000010)
SDL_INIT_VIDEO = const(0x00000020)
SDL_INIT_JOYSTICK = const(0x00000200)
SDL_INIT_HAPTIC = const(0x00001000)
SDL_INIT_GAMECONTROLLER = const(0x00002000)
SDL_INIT_EVENTS = const(0x00004000)
SDL_INIT_EVERYTHING = const(0x0000000F)
SDL_INIT_NOPARACHUTE = const(0x00100000)

# SDL_Texture values
SDL_TEXTUREACCESS_STATIC = const(0)
SDL_TEXTUREACCESS_STREAMING = const(1)
SDL_TEXTUREACCESS_TARGET = const(2)

# SDL_BlendMode values
SDL_BLENDMODE_NONE = const(1)
SDL_BLENDMODE_BLEND = const(2)
SDL_BLENDMODE_ADD = const(3)
SDL_BLENDMODE_MOD = const(4)
SDL_BLENDMODE_MUL = const(5)

# SDL_Event types (not complete)
SDL_QUIT = const(0x100)                     # User clicked the window close button
SDL_KEYDOWN = const(0x300)                  # Key pressed
SDL_KEYUP = const(0x301)                    # Key released
SDL_MOUSEMOTION = const(0x400)              # Mouse moved
SDL_MOUSEBUTTONDOWN = const(0x401)          # Mouse button pressed
SDL_MOUSEBUTTONUP = const(0x402)            # Mouse button released
SDL_MOUSEWHEEL = const(0x403)               # Mouse wheel motion
SDL_POLLSENTINEL = const(0x7F00)            # Signals the end of an event poll cycle

# SDL_MouseMotionEvent button masks
SDL_BUTTON_LMASK = const(1 << 0)           # Left mouse button
SDL_BUTTON_MMASK = const(1 << 1)           # Middle mouse button
SDL_BUTTON_RMASK = const(1 << 2)           # Right mouse button

# SDL_Keycode mod values (not complete)
KMOD_NONE = const(0x0000)
KMOD_LSHIFT = const(0x0001)
KMOD_RSHIFT = const(0x0002)
KMOD_LCTRL = const(0x0040)
KMOD_RCTRL = const(0x0080)
KMOD_LALT = const(0x0100)
KMOD_RALT = const(0x0200)
KMOD_LGUI = const(0x0400)
KMOD_RGUI = const(0x0800)
KMOD_NUM = const(0x1000)
KMOD_CAPS = const(0x2000)
KMOD_MODE = const(0x4000)
KMOD_CTRL = KMOD_LCTRL | KMOD_RCTRL
KMOD_SHIFT = KMOD_LSHIFT | KMOD_RSHIFT
KMOD_ALT = KMOD_LALT | KMOD_RALT
KMOD_GUI = KMOD_LGUI | KMOD_RGUI


###############################################################################
#                          SDL2 functions                                     #
###############################################################################

# Access the SDL2 shared library
_sdl = ffi.open("libSDL2-2.0.so.0")

# SDL misc functions
SDL_Init = _sdl.func("i", "SDL_Init", "I")
SDL_Quit = _sdl.func("v", "SDL_Quit", "")
SDL_GetKeyName = _sdl.func("s", "SDL_GetKeyName", "i")
SDL_GetKeyFromName = _sdl.func("i", "SDL_GetKeyFromName", "s")
SDL_PollEvent = _sdl.func("i", "SDL_PollEvent", "P")
SDL_GetError = _sdl.func("s", "SDL_GetError", "")

# SDL window functions
SDL_CreateWindow = _sdl.func("P", "SDL_CreateWindow", "siiiii")
SDL_DestroyWindow = _sdl.func("v", "SDL_DestroyWindow", "P")
SDL_SetWindowSize = _sdl.func("v", "SDL_SetWindowSize", "Pii")

# SDL renderer functions
SDL_CreateRenderer = _sdl.func("P", "SDL_CreateRenderer", "PiI")
SDL_DestroyRenderer = _sdl.func("v", "SDL_DestroyRenderer", "P")
SDL_SetRenderDrawColor = _sdl.func("i", "SDL_SetRenderDrawColor", "PPPP")
SDL_SetRenderTarget = _sdl.func("i", "SDL_SetRenderTarget", "pP")
SDL_RenderClear = _sdl.func("v", "SDL_RenderClear", "P")
SDL_RenderCopy = _sdl.func("v", "SDL_RenderCopy", "PPPP")
SDL_RenderPresent = _sdl.func("v", "SDL_RenderPresent", "P")
SDL_RenderFillRect = _sdl.func("i", "SDL_RenderFillRect", "PP")
SDL_RenderSetLogicalSize = _sdl.func("i", "SDL_RenderSetLogicalSize", "Pii")

# SDL texture functions
SDL_CreateTexture = _sdl.func("P", "SDL_CreateTexture", "PIiiii")
SDL_DestroyTexture = _sdl.func("v", "SDL_DestroyTexture", "P")
SDL_SetTextureBlendMode = _sdl.func("i", "SDL_SetTextureBlendMode", "PI")
SDL_UpdateTexture = _sdl.func("i", "SDL_UpdateTexture", "PPPi")


###############################################################################
#                          Helper functions                                   #
###############################################################################

def SDL_Rect(x=0, y=0, w=0, h=0):
    # Create an SDL_Rect object
    return struct.pack("iiii", x, y, w, h)

def retcheck(retvalue):
    # Check the return value of an SDL function and raise an exception if it's not 0
    if retvalue:
        raise RuntimeError(SDL_GetError())


###############################################################################
#                          LCD class                                      #
###############################################################################

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
        title="MicroPython",
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

        self._event = bytearray(56)  # The largest size of an SDL_Event struct

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
        self.win = SDL_CreateWindow(title, x, y, int(self.width*scale), int(self.height*scale), window_flags)
        if not self.win:
            raise RuntimeError(f"{SDL_GetError()}")

        self.renderer = SDL_CreateRenderer(self.win, -1, render_flags)
        if not self.renderer:
            raise RuntimeError(f"{SDL_GetError()}")

        self.requires_byte_swap = False

        self._init()

    def _init(self):
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

        retcheck(SDL_SetWindowSize(self.win, int(self.width*self._scale), int(self.height*self._scale)))
        retcheck(SDL_DestroyTexture(self.texture))
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
        pitch = int(w * self.color_depth // 8)
        if len(buffer) != pitch * h:
            raise ValueError("Buffer size does not match dimensions")
        blitRect = SDL_Rect(x, y, w, h)
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
        Deinitializes the sdl2lcd instance.
        """
        retcheck(SDL_DestroyTexture(self.texture))
        retcheck(SDL_DestroyRenderer(self.renderer))
        retcheck(SDL_DestroyWindow(self.win))
        retcheck(SDL_Quit())

    def __del__(self):
        """
        Deinitializes the sdl2lcd instance.
        """
        self.deinit()

    def poll_event(self):
        """
        Polls for an event and returns the event type and data.

        :return: The event type and data.
        :rtype: tuple
        """
        if (event := super().poll_event()) is not None:
            return event
        if SDL_PollEvent(self._event):
            event_type = int.from_bytes(self._event[:4], 'little')
            if event_type in Events.types:
                event = SDL_Event.from_bytes(self._event)
                # print(f"{event=}")
                if event.type == Events.QUIT:
                    self.quit_func()
                return event
        return None


###############################################################################
#                          SDL_Event class                                    #
###############################################################################

class SDL_Event:
    """
    SDL2's SDL_Event type is a union of several structs. The largest of these
    is 56 bytes long. The following structs are used to access the fields of
    the SDL_Event struct.
    """
    @staticmethod
    def from_bytes(event_bytes):
        """
        Return an event struct based on the event type
        The type is the first 4 bytes of the event

        :param e: The event.
        :type e: bytearray
        :return: The event struct.
        :rtype: uctypes.struct
        """
        event_type = int.from_bytes(event_bytes[:4], 'little')
        try:
            e = uctypes.struct(uctypes.addressof(event_bytes), SDL_Event.struct_map[event_type])
        except KeyError:
            e = uctypes.struct(uctypes.addressof(event_bytes), SDL_Event.SDL_CommonEvent)

        if event_type == SDL_MOUSEMOTION:
            l = 1 if e.motion.state & SDL_BUTTON_LMASK else 0
            m = 1 if e.motion.state & SDL_BUTTON_MMASK else 0
            r = 1 if e.motion.state & SDL_BUTTON_RMASK else 0
            evt = Events.Motion(e.type, (e.motion.x, e.motion.y), (e.motion.xrel, e.motion.yrel), (l, m, r), e.motion.which != 0, e.motion.windowID)
        elif event_type in (SDL_MOUSEBUTTONDOWN, SDL_MOUSEBUTTONUP):
            evt = Events.Button(e.type, (e.button.x, e.button.y), e.button.button, e.button.which != 0, e.button.windowID)
        elif event_type == SDL_MOUSEWHEEL:
            evt = Events.Wheel(e.type, e.wheel.direction != 0, e.wheel.x, e.wheel.y, e.wheel.preciseX, e.wheel.preciseY, e.wheel.which != 0, e.wheel.windowID)
        elif event_type in (SDL_KEYDOWN, SDL_KEYUP):
            name = SDL_GetKeyName(e.key.keysym.sym)
            evt = Events.Key(e.type, name, e.key.keysym.sym, e.key.keysym.mod, e.key.keysym.scancode, e.key.windowID)
        else:
            evt = Events.Unknown(e.type)

        return evt

    # Define struct fields for SDL_CommonEvent
    SDL_CommonEvent = {
        "type": uctypes.UINT32 | 0,
        "timestamp": uctypes.UINT32 | 4,
    }

    # Define struct fields for SDL_KeyboardEvent
    SDL_KeyboardEvent = {
        "type": uctypes.UINT32 | 0,
        "timestamp": uctypes.UINT32 | 4,
        "key": (8, {
            "windowID": uctypes.UINT32 | 0,
            "state": uctypes.UINT8 | 4,
            "repeat": uctypes.UINT8 | 5,
            "padding2": uctypes.UINT8 | 6,
            "padding3": uctypes.UINT8 | 7,
            "keysym": (8, {
                "scancode": 0 | uctypes.UINT32,
                "sym": 4 | uctypes.UINT32,
                "mod": 8 | uctypes.UINT16,
                "unused": 10 | uctypes.UINT32,
            })
        })
    }

    # Define struct fields for SDL_MouseMotionEvent
    SDL_MouseMotionEvent = {
        "type": uctypes.UINT32 | 0,
        "timestamp": uctypes.UINT32 | 4,
        "motion": (8, {
            "windowID": uctypes.UINT32 | 0,
            "which": uctypes.UINT32 | 4,
            "state": uctypes.UINT32 | 8,
            "x": uctypes.INT32 | 12,
            "y": uctypes.INT32 | 16,
            "xrel": uctypes.INT32 | 20,
            "yrel": uctypes.INT32 | 8,
        })
    }

    # Define struct fields for SDL_MouseButtonEvent
    SDL_MouseButtonEvent = {
        "type": uctypes.UINT32 | 0,
        "timestamp": uctypes.UINT32 | 4,
        "button": (8, {
            "windowID": uctypes.UINT32 | 0,
            "which": uctypes.UINT32 | 4,
            "button": uctypes.UINT8 | 8,
            "state": uctypes.UINT8 | 9,
            "clicks": uctypes.UINT8 | 10,
            "padding1": uctypes.UINT8 | 11,
            "x": uctypes.INT32 | 12,
            "y": uctypes.INT32 | 16,
        })
    }

    # Define struct fields for SDL_MouseWheelEvent
    SDL_MouseWheelEvent = {
        "type": uctypes.UINT32 | 0,
        "timestamp": uctypes.UINT32 | 4,
        "wheel": (8, {
            "windowID": uctypes.UINT32 | 0,
            "which": uctypes.UINT32 | 4,
            "x": uctypes.INT32 | 8,
            "y": uctypes.INT32 | 12,
            "direction": uctypes.UINT32 | 16,
            "preciseX": uctypes.FLOAT32 | 20,
            "preciseY": uctypes.FLOAT32 | 24,
        })
    }

    # SDL_Event type to event struct mapping for event_type_from_bytes()
    struct_map = {
        SDL_KEYDOWN: SDL_KeyboardEvent,
        SDL_KEYUP: SDL_KeyboardEvent,
        SDL_MOUSEMOTION: SDL_MouseMotionEvent,
        SDL_MOUSEBUTTONDOWN: SDL_MouseButtonEvent,
        SDL_MOUSEBUTTONUP: SDL_MouseButtonEvent,
        SDL_MOUSEWHEEL: SDL_MouseWheelEvent,
        SDL_POLLSENTINEL: SDL_CommonEvent,
    }


###############################################################################
#                          SDL2 Pixel Formats                                 #
###############################################################################

def SDL_DEFINE_PIXELFORMAT(type, order, layout, bits, bytes):
    """
    Define a pixel format.
    """
    return ((1 << 28) | ((type) << 24) | ((order) << 20) | ((layout) << 16) | \
        ((bits) << 8) | ((bytes) << 0))

# SDL_PIXELTYPE values
SDL_PIXELTYPE_UNKNOWN = const(0)
SDL_PIXELTYPE_INDEX1 = const(1)
SDL_PIXELTYPE_INDEX4 = const(2)
SDL_PIXELTYPE_INDEX8 = const(3)
SDL_PIXELTYPE_PACKED8 = const(4)
SDL_PIXELTYPE_PACKED16 = const(5)
SDL_PIXELTYPE_PACKED32 = const(6)
SDL_PIXELTYPE_ARRAYU8 = const(7)
SDL_PIXELTYPE_ARRAYU16 = const(8)
SDL_PIXELTYPE_ARRAYU32 = const(9)
SDL_PIXELTYPE_ARRAYF16 = const(10)
SDL_PIXELTYPE_ARRAYF32 = const(11)

# SDL_PACKEDORDER values
SDL_PACKEDORDER_NONE = const(0)
SDL_PACKEDORDER_XRGB = const(1)
SDL_PACKEDORDER_RGBX = const(2)
SDL_PACKEDORDER_ARGB = const(3)
SDL_PACKEDORDER_RGBA = const(4)
SDL_PACKEDORDER_XBGR = const(5)
SDL_PACKEDORDER_BGRX = const(6)
SDL_PACKEDORDER_ABGR = const(7)
SDL_PACKEDORDER_BGRA = const(8)

# SDL_ARRAYORDER values
SDL_ARRAYORDER_NONE = const(0)
SDL_ARRAYORDER_RGB = const(1)
SDL_ARRAYORDER_RGBA = const(2)
SDL_ARRAYORDER_ARGB = const(3)
SDL_ARRAYORDER_BGR = const(4)
SDL_ARRAYORDER_BGRA = const(5)
SDL_ARRAYORDER_ABGR = const(6)

# SDL_PACKEDLAYOUT values
SDL_PACKEDLAYOUT_NONE = const(0)
SDL_PACKEDLAYOUT_332 = const(1)
SDL_PACKEDLAYOUT_4444 = const(2)
SDL_PACKEDLAYOUT_1555 = const(3)
SDL_PACKEDLAYOUT_5551 = const(4)
SDL_PACKEDLAYOUT_565 = const(5)
SDL_PACKEDLAYOUT_8888 = const(6)
SDL_PACKEDLAYOUT_2101010 = const(7)
SDL_PACKEDLAYOUT_1010102 = const(8)

# SDL_BITMAPORDER values
SDL_BITMAPORDER_NONE = const(0)
SDL_BITMAPORDER_4321 = const(1)
SDL_BITMAPORDER_1234 = const(2)

# SDL_PIXELFORMAT values
SDL_PIXELFORMAT_UNKNOWN = const(0)
SDL_PIXELFORMAT_INDEX1LSB = \
    SDL_DEFINE_PIXELFORMAT(SDL_PIXELTYPE_INDEX1, SDL_BITMAPORDER_4321, 0,
                            1, 0)
SDL_PIXELFORMAT_INDEX1MSB = \
    SDL_DEFINE_PIXELFORMAT(SDL_PIXELTYPE_INDEX1, SDL_BITMAPORDER_1234, 0,
                            1, 0)
SDL_PIXELFORMAT_INDEX4LSB = \
    SDL_DEFINE_PIXELFORMAT(SDL_PIXELTYPE_INDEX4, SDL_BITMAPORDER_4321, 0,
                            4, 0)
SDL_PIXELFORMAT_INDEX4MSB = \
    SDL_DEFINE_PIXELFORMAT(SDL_PIXELTYPE_INDEX4, SDL_BITMAPORDER_1234, 0,
                            4, 0)
SDL_PIXELFORMAT_INDEX8 = \
    SDL_DEFINE_PIXELFORMAT(SDL_PIXELTYPE_INDEX8, 0, 0, 8, 1)
SDL_PIXELFORMAT_RGB332 = \
    SDL_DEFINE_PIXELFORMAT(SDL_PIXELTYPE_PACKED8, SDL_PACKEDORDER_XRGB,
                            SDL_PACKEDLAYOUT_332, 8, 1)
SDL_PIXELFORMAT_XRGB4444 = \
    SDL_DEFINE_PIXELFORMAT(SDL_PIXELTYPE_PACKED16, SDL_PACKEDORDER_XRGB,
                            SDL_PACKEDLAYOUT_4444, 12, 2)
SDL_PIXELFORMAT_RGB444 = SDL_PIXELFORMAT_XRGB4444
SDL_PIXELFORMAT_XBGR4444 = \
    SDL_DEFINE_PIXELFORMAT(SDL_PIXELTYPE_PACKED16, SDL_PACKEDORDER_XBGR,
                            SDL_PACKEDLAYOUT_4444, 12, 2)
SDL_PIXELFORMAT_BGR444 = SDL_PIXELFORMAT_XBGR4444
SDL_PIXELFORMAT_XRGB1555 = \
    SDL_DEFINE_PIXELFORMAT(SDL_PIXELTYPE_PACKED16, SDL_PACKEDORDER_XRGB,
                            SDL_PACKEDLAYOUT_1555, 15, 2)
SDL_PIXELFORMAT_RGB555 = SDL_PIXELFORMAT_XRGB1555
SDL_PIXELFORMAT_XBGR1555 = \
    SDL_DEFINE_PIXELFORMAT(SDL_PIXELTYPE_PACKED16, SDL_PACKEDORDER_XBGR,
                            SDL_PACKEDLAYOUT_1555, 15, 2)
SDL_PIXELFORMAT_BGR555 = SDL_PIXELFORMAT_XBGR1555
SDL_PIXELFORMAT_ARGB4444 = \
    SDL_DEFINE_PIXELFORMAT(SDL_PIXELTYPE_PACKED16, SDL_PACKEDORDER_ARGB,
                            SDL_PACKEDLAYOUT_4444, 16, 2)
SDL_PIXELFORMAT_RGBA4444 = \
    SDL_DEFINE_PIXELFORMAT(SDL_PIXELTYPE_PACKED16, SDL_PACKEDORDER_RGBA,
                            SDL_PACKEDLAYOUT_4444, 16, 2)
SDL_PIXELFORMAT_ABGR4444 = \
    SDL_DEFINE_PIXELFORMAT(SDL_PIXELTYPE_PACKED16, SDL_PACKEDORDER_ABGR,
                            SDL_PACKEDLAYOUT_4444, 16, 2)
SDL_PIXELFORMAT_BGRA4444 = \
    SDL_DEFINE_PIXELFORMAT(SDL_PIXELTYPE_PACKED16, SDL_PACKEDORDER_BGRA,
                            SDL_PACKEDLAYOUT_4444, 16, 2)
SDL_PIXELFORMAT_ARGB1555 = \
    SDL_DEFINE_PIXELFORMAT(SDL_PIXELTYPE_PACKED16, SDL_PACKEDORDER_ARGB,
                            SDL_PACKEDLAYOUT_1555, 16, 2)
SDL_PIXELFORMAT_RGBA5551 = \
    SDL_DEFINE_PIXELFORMAT(SDL_PIXELTYPE_PACKED16, SDL_PACKEDORDER_RGBA,
                            SDL_PACKEDLAYOUT_5551, 16, 2)
SDL_PIXELFORMAT_ABGR1555 = \
    SDL_DEFINE_PIXELFORMAT(SDL_PIXELTYPE_PACKED16, SDL_PACKEDORDER_ABGR,
                            SDL_PACKEDLAYOUT_1555, 16, 2)
SDL_PIXELFORMAT_BGRA5551 = \
    SDL_DEFINE_PIXELFORMAT(SDL_PIXELTYPE_PACKED16, SDL_PACKEDORDER_BGRA,
                            SDL_PACKEDLAYOUT_5551, 16, 2)
SDL_PIXELFORMAT_RGB565 = \
    SDL_DEFINE_PIXELFORMAT(SDL_PIXELTYPE_PACKED16, SDL_PACKEDORDER_XRGB,
                            SDL_PACKEDLAYOUT_565, 16, 2)
SDL_PIXELFORMAT_BGR565 = \
    SDL_DEFINE_PIXELFORMAT(SDL_PIXELTYPE_PACKED16, SDL_PACKEDORDER_XBGR,
                            SDL_PACKEDLAYOUT_565, 16, 2)
SDL_PIXELFORMAT_RGB24 = \
    SDL_DEFINE_PIXELFORMAT(SDL_PIXELTYPE_ARRAYU8, SDL_ARRAYORDER_RGB, 0,
                            24, 3)
SDL_PIXELFORMAT_BGR24 = \
    SDL_DEFINE_PIXELFORMAT(SDL_PIXELTYPE_ARRAYU8, SDL_ARRAYORDER_BGR, 0,
                            24, 3)
SDL_PIXELFORMAT_XRGB8888 = \
    SDL_DEFINE_PIXELFORMAT(SDL_PIXELTYPE_PACKED32, SDL_PACKEDORDER_XRGB,
                            SDL_PACKEDLAYOUT_8888, 24, 4)
SDL_PIXELFORMAT_RGB888 = SDL_PIXELFORMAT_XRGB8888
SDL_PIXELFORMAT_RGBX8888 = \
    SDL_DEFINE_PIXELFORMAT(SDL_PIXELTYPE_PACKED32, SDL_PACKEDORDER_RGBX,
                            SDL_PACKEDLAYOUT_8888, 24, 4)
SDL_PIXELFORMAT_XBGR8888 = \
    SDL_DEFINE_PIXELFORMAT(SDL_PIXELTYPE_PACKED32, SDL_PACKEDORDER_XBGR,
                            SDL_PACKEDLAYOUT_8888, 24, 4)
SDL_PIXELFORMAT_BGR888 = SDL_PIXELFORMAT_XBGR8888
SDL_PIXELFORMAT_BGRX8888 = \
    SDL_DEFINE_PIXELFORMAT(SDL_PIXELTYPE_PACKED32, SDL_PACKEDORDER_BGRX,
                            SDL_PACKEDLAYOUT_8888, 24, 4)
SDL_PIXELFORMAT_ARGB8888 = \
    SDL_DEFINE_PIXELFORMAT(SDL_PIXELTYPE_PACKED32, SDL_PACKEDORDER_ARGB,
                            SDL_PACKEDLAYOUT_8888, 32, 4)
SDL_PIXELFORMAT_RGBA8888 = \
    SDL_DEFINE_PIXELFORMAT(SDL_PIXELTYPE_PACKED32, SDL_PACKEDORDER_RGBA,
                            SDL_PACKEDLAYOUT_8888, 32, 4)
SDL_PIXELFORMAT_ABGR8888 = \
    SDL_DEFINE_PIXELFORMAT(SDL_PIXELTYPE_PACKED32, SDL_PACKEDORDER_ABGR,
                            SDL_PACKEDLAYOUT_8888, 32, 4)
SDL_PIXELFORMAT_BGRA8888 = \
    SDL_DEFINE_PIXELFORMAT(SDL_PIXELTYPE_PACKED32, SDL_PACKEDORDER_BGRA,
                            SDL_PACKEDLAYOUT_8888, 32, 4)
SDL_PIXELFORMAT_ARGB2101010 = \
    SDL_DEFINE_PIXELFORMAT(SDL_PIXELTYPE_PACKED32, SDL_PACKEDORDER_ARGB,
                            SDL_PACKEDLAYOUT_2101010, 32, 4)
