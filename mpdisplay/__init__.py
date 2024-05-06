# SPDX-FileCopyrightText: 2024 Brad Barnett
#
# SPDX-License-Identifier: MIT
import sys
from ._basedisplay import _BaseDisplay
from ._devices import Devices
from ._events import Events
from ._keys import Keys


if sys.implementation.name == "cpython":
    import platform
    if platform.uname().node == "penguin":  # ChromeOS
        from ._pgdisplay import PGDisplay as DesktopDisplay, PGEvents as DesktopEvents
    else:
        from ._sdl2display import SDL2Display as DesktopDisplay, SDL2Events as DesktopEvents
elif sys.implementation.name == "micropython":
    if sys.platform == "linux":
        from ._sdl2display import SDL2Display as DesktopDisplay, SDL2Events as DesktopEvents
    else:
        from ._busdisplay import BusDisplay
elif sys.implementation.name == "circuitpython":
    from ._busdisplay import BusDisplay
else:
    raise ImportError("unsupported Python implementation")
