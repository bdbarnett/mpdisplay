# SPDX-FileCopyrightText: 2024 Brad Barnett
#
# SPDX-License-Identifier: MIT
from collections import namedtuple
from micropython import const


class Events:
    # Event types (from SDL2 / PyGame, not complete)
    QUIT = const(0x100)  # User clicked the window close button
    KEYDOWN = const(0x300)  # Key pressed
    KEYUP = const(0x301)  # Key released
    MOUSEMOTION = const(0x400)  # Mouse moved
    MOUSEBUTTONDOWN = const(0x401)  # Mouse button pressed
    MOUSEBUTTONUP = const(0x402)  # Mouse button released
    MOUSEWHEEL = const(0x403)  # Mouse wheel motion

    types = [
        QUIT,
        KEYDOWN,
        KEYUP,
        MOUSEMOTION,
        MOUSEBUTTONDOWN,
        MOUSEBUTTONUP,
        MOUSEWHEEL,
    ]

    # Event classes
    Unknown = namedtuple("Common", "type")
    Motion = namedtuple("Motion", "type pos rel buttons touch window")
    Button = namedtuple("Button", "type pos button touch window")
    Wheel = namedtuple("Wheel", "type flipped x y precise_x precise_y touch window")
    Key = namedtuple( "Key", "type name key mod scancode window")  # SDL2 provides key `name`, PyGame provides `unicode`
                                                                   # Use `key` and `mod` for portable code
