# SPDX-FileCopyrightText: 2024 Brad Barnett
#
# SPDX-License-Identifier: MIT
from sys import implementation, platform
from ._basedisplay import _BaseDisplay
from ._devices import Devices
from ._events import Events
from ._keys import Keys


if implementation.name == "cpython":
    from ._pgdisplay import *
elif implementation.name == "circuitpython":
    from ._busdisplay import *
elif implementation.name == "micropython":
    if platform == "linux":
        from ._sdl2display import *
    else:
        from ._busdisplay import *
else:
    raise ImportError("unsupported Python implementation")
