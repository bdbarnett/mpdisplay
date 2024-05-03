# SPDX-FileCopyrightText: 2024 Brad Barnett
#
# SPDX-License-Identifier: MIT
"""
An implementation of SDL2 written in MicroPython.
"""

import uctypes
import ffi
import struct
from micropython import const
from collections import namedtuple


###############################################################################
#                          SDL2 Constants                                     #
###############################################################################

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
SDL_GetError = _sdl.func("s", "SDL_GetError", "")
SDL_PollEvent = _sdl.func("i", "SDL_PollEvent", "P")

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
#                          SDL2 Event structs                                 #
###############################################################################

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
_struct_map = {
    SDL_KEYDOWN: SDL_KeyboardEvent,
    SDL_KEYUP: SDL_KeyboardEvent,
    SDL_MOUSEMOTION: SDL_MouseMotionEvent,
    SDL_MOUSEBUTTONDOWN: SDL_MouseButtonEvent,
    SDL_MOUSEBUTTONUP: SDL_MouseButtonEvent,
    SDL_MOUSEWHEEL: SDL_MouseWheelEvent,
    SDL_POLLSENTINEL: SDL_CommonEvent,
}


###############################################################################
#                          Helper functions                                   #
###############################################################################

def SDL_Event(event_bytes=None):
    """
    SDL2's SDL_Event type is a union of several structs. The largest of these
    is 56 bytes long. The following structs are used to access the fields of
    the SDL_Event struct.

    Return an event struct based on the event type
    The type is the first 4 bytes of the event

    :param e: The event.
    :type e: bytearray
    :return: The event struct.
    :rtype: uctypes.struct
    """
    if event_bytes is None:
        return bytearray(56)  # The largest size of an SDL_Event struct

    event_type = int.from_bytes(event_bytes[:4], 'little')
    try:
        return uctypes.struct(uctypes.addressof(event_bytes), _struct_map[event_type])
    except KeyError:
        return uctypes.struct(uctypes.addressof(event_bytes), SDL_CommonEvent)

def SDL_Rect(x=0, y=0, w=0, h=0):
    # Create an SDL_Rect object
    return struct.pack("iiii", x, y, w, h)


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
