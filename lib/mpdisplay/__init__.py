from sys import implementation, platform

if implementation.name == "cpython":
    from ._pgdisplay import *
elif implementation.name == "micropython":
    if platform == "linux":
        from ._sdl2display import *
    else:
        from ._busdisplay import *
else:
    raise ImportError("Unsupported Python implementation")
