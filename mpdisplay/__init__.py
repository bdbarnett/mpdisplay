# SPDX-FileCopyrightText: 2024 Brad Barnett
#
# SPDX-License-Identifier: MIT
import sys
from ._basedisplay import _BaseDisplay
from ._devices import Devices
from ._events import Events
from ._keys import Keys

"""
Import flowchart:

Is it CPython?
    Yes, is it ChromeOS?
        Yes, import PGDisplay
        No, try to import SDL2Display
            If fail, print error and import PGDisplay
Is it MicroPython?
    Yes, is it Linux?
        Yes, try to import SDL2Display
            If fail, print error and import PGDisplay
        No, import BusDisplay
Is it CircuitPython?
    Yes, import BusDisplay
Else, raise ImportError
"""

if sys.implementation.name == "cpython":
    import platform
    if platform.uname().node == "penguin":  # ChromeOS
        from ._pgdisplay import PGDisplay as DesktopDisplay, PGEvents as DesktopEvents
    else:
        try:
            from ._sdl2display import SDL2Display as DesktopDisplay, SDL2Events as DesktopEvents
        except Exception as e:
            print(f"MPDisplay: Error loading SDL2Display -- {e}")
            print("    Falling back to PGDisplay")
            from ._pgdisplay import PGDisplay as DesktopDisplay, PGEvents as DesktopEvents
elif sys.implementation.name == "micropython":
    if sys.platform == "linux":
        try:
            from ._sdl2display import SDL2Display as DesktopDisplay, SDL2Events as DesktopEvents
        except Exception as e:
            print(f"MPDisplay:  Error loading SDL2Display -- {e}")
            print("    Falling back to PGDisplay")
            from ._pgdisplay import PGDisplay as DesktopDisplay, PGEvents as DesktopEvents
    else:
        from ._busdisplay import BusDisplay
elif sys.implementation.name == "circuitpython":
    from ._busdisplay import BusDisplay
else:
    raise ImportError("unsupported Python implementation")
