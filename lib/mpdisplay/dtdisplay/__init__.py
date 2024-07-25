"""
dtdisplay - autoloads either SDLDisplay or PGDisplay
"""
from .. import _BaseDisplay, events_enabled, Area  # noqa: F401
if events_enabled:
    from .. import Events, Devices  # noqa: F401

class DTDisplay():
    def __new__(cls, *args, **kwargs):
        try:
            from .sdldisplay import SDLDisplay
            instance = SDLDisplay(*args, **kwargs)
        except Exception as e:
            import sys
            if sys.implementation.name == "micropython":
                raise Exception(e)
            else:
                from .pgdisplay import PGDisplay
                instance = PGDisplay(*args, **kwargs)
        return instance
