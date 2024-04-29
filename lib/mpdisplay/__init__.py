from sys import implementation, platform
from ._basedisplay import _BaseDisplay
from ._devices import Devices
from ._events import Events


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
