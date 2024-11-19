# SPDX-FileCopyrightText: 2024 Brad Barnett
#
# SPDX-License-Identifier: MIT
"""
`eventsys`
====================================================
An Event System including event types and device types for *Python.
"""

from micropython import const
from collections import namedtuple


class Events:
    """
    A container for event types and classes.  Similar to a C enum and struct.
    """

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
    _USER_TYPE_BASE = 0x8000

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
    Key = namedtuple("Key", "type name key mod scancode window")
    Quit = namedtuple("Quit", "type")
    Any = namedtuple("Any", "type")

    @staticmethod
    def new(types: list[str | tuple[str, int]] = [], classes: dict[str, str] = {}):
        """
        Create new event types and classes for the Events class.

        For example, to create the events for the keypad device:
        ```
        from eventsys import Events

        types = [("KEYDOWN", 0x300), ("KEYUP", 0x301)]
        classes = {
            "Key": "type name key mod scancode window",
        }
        Events.new_types(types, classes)

        # Optionally update the filter
        Events.filter += [Events.KEYDOWN, Events.KEYUP]
        ```

        Args:
            types (list[str | tuple[str, int]]): List of event types or tuples of event type and value.
                If a value is not provided, the next available value will be used.
            classes (dict[str, str]): Dictionary of event classes and fields.
        """
        for type_name in types:
            if isinstance(type_name, tuple):
                type_name, value = type_name
            else:
                value = None
            type_name = type_name.upper()
            if hasattr(Events, type_name):
                raise ValueError(f"Event type {type_name} already exists in Events class.")
            else:
                setattr(Events, type_name, value if value else Events._USER_TYPE_BASE)
                if not value:
                    Events._USER_TYPE_BASE += 1

        for event_class_name, event_class_fields in classes.items():
            event_class_name = event_class_name[0].upper() + event_class_name[1:].lower()
            if hasattr(Events, event_class_name):
                raise ValueError(f"Event class {event_class_name} already exists in Events class.")
            else:
                event_class_fields = event_class_fields.lower()
                setattr(
                    Events,
                    event_class_name,
                    namedtuple(event_class_name, event_class_fields),
                )
