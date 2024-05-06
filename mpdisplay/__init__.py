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
- Create a device driver instance: `events_drv = mpdisplay.DesktopEvents()`
- Create a device registration with the display: `events_dev = display_drv.create_device(read=events_drv.read)`
- Use display_drv to interact with the display and all registered devices.

If no display drivers are available, an ImportError will be raised.
"""

import sys
import os
from ._basedisplay import _BaseDisplay
from ._devices import Devices
from ._events import Events
from ._keys import Keys


if (sys.implementation.name != "micropython") and (envsetting := os.getenv("MPDISPLAY")):
    if envsetting == "SDL2Display":
        import sdl2_lib as sdl2
        from ._sdl2display import SDL2Display as DesktopDisplay, SDL2Events as DesktopEvents
    elif envsetting == "PGDisplay":
        import pygame as pg
        from ._pgdisplay import PGDisplay as DesktopDisplay, PGEvents as DesktopEvents, pg
    elif envsetting == "BusDisplay":
        from ._busdisplay import BusDisplay
    else:
        raise ImportError(f"unsupported environment setting MPDISPLAY={envsetting}")
else:
    try:
        import sdl2_lib as sdl2
        from ._sdl2display import SDL2Display as DesktopDisplay, SDL2Events as DesktopEvents
    except:
        try:
            import pygame as pg
            from ._pgdisplay import PGDisplay as DesktopDisplay, PGEvents as DesktopEvents
        except:
            try:
                from ._busdisplay import BusDisplay
            except:
                raise ImportError("MPDisplay: No display drivers available")
