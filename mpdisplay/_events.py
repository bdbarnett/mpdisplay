# SPDX-FileCopyrightText: 2024 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""
Events class for MPDisplay.
"""

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
    JOYAXISMOTION = const(0x600)  # Joystick axis motion
    JOYBALLMOTION = const(0x601)  # Joystick trackball motion
    JOYHATMOTION = const(0x602)  # Joystick hat position change
    JOYBUTTONDOWN = const(0x603)  # Joystick button pressed
    JOYBUTTONUP = const(0x604)  # Joystick button released

    filter = [
        QUIT,
        KEYDOWN,
        KEYUP,
        MOUSEMOTION,
        MOUSEBUTTONDOWN,
        MOUSEBUTTONUP,
        MOUSEWHEEL,
    ]

    # Event classes from PyGame
    Unknown = namedtuple("Common", "type")
    Motion = namedtuple("Motion", "type pos rel buttons touch window")
    Button = namedtuple("Button", "type pos button touch window")
    Wheel = namedtuple("Wheel", "type flipped x y precise_x precise_y touch window")
    Key = namedtuple( "Key", "type name key mod scancode window")
    Quit = namedtuple( "Quit", "type")
