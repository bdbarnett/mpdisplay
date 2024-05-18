# SPDX-FileCopyrightText: 2024 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""
MPDisplay is a module that provides a display interface for various environments. It allows you to interact with different display devices and handle events.

Supported display classes:
- 'SDL2Display': Uses SDL2 library for display and event handling.
- 'PGDisplay': Uses Pygame library for display and event handling.
- 'BusDisplay': Uses a bus library such as lcd_bus or CircuitPython's DisplayIO buses for communication and handles communication with touch, encoder and keypad devices.

If the 'MPDISPLAY' environment variable is set to one of the above clsses, this module will load that class. Otherwise, it will try to load them in the order listed.

Note: Make sure to install the required dependencies for the chosen display class.

Usage:
- Import the module: `import mpdisplay`
- Create an instance of the display: `display_drv = mpdisplay.DesktopDisplay()`
- Create a device driver instance: `events_drv = mpdisplay.EventQueue()`
- Create a device registration with the display: `events_dev = display_drv.create_device(read=events_drv.read)`
- Use display_drv to interact with the display and all registered devices.

If no display drivers are available, an ImportError will be raised.
"""

import sys
import os
from eventsys.devices import Devices, Broker
from eventsys.events import Events
from eventsys.keys import Keys
from ._basedisplay import _BaseDisplay


if (sys.implementation.name != "micropython") and (envsetting := os.getenv("MPDisplay")):
    if envsetting == "SDL2Display":
        print("MPDisplay: Using SDL2Display per MPDisplay environment variable.\n")
        import sdl2_lib as sdl2
        from ._sdl2display import SDL2Display as DesktopDisplay, SDL2EventQueue as EventQueue
    elif envsetting == "PGDisplay":
        print("MPDisplay: Using PGDisplay per MPDisplay environment variable.\n")
        import pygame as pg
        from ._pgdisplay import PGDisplay as DesktopDisplay, PGEventQueue as EventQueue, pg
    elif envsetting == "BusDisplay":
        print("MPDisplay: Using BusDisplay per MPDisplay environment variable.\n")
        from ._busdisplay import BusDisplay
    else:
        raise ImportError(f"unsupported environment setting MPDISPLAY={envsetting}")
else:
    try:
        from ._busdisplay import BusDisplay
    except Exception as e:
        print(f"MPDisplay: {e}")
        print("MPDisplay: Trying SDL2Display...")
        try:
            import sdl2_lib as sdl2
            from ._sdl2display import SDL2Display as DesktopDisplay, SDL2EventQueue as EventQueue
        except Exception as e:
            print(f"MPDisplay: {e}")
            print("MPDisplay: Trying Pygame...")
            try:
                import pygame as pg
                from ._pgdisplay import PGDisplay as DesktopDisplay, PGEventQueue as EventQueue
            except Exception as e:
                print(f"MPDisplay: {e}")
                raise ImportError("MPDisplay: No display drivers available")

print("MPDisplay: display driver loaded.")