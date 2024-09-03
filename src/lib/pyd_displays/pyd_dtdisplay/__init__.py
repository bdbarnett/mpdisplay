"""
pyd_dtdisplay - autoloads either SDLDisplay or PGDisplay
"""
from pyd_basedisplay import BaseDisplay, Area, color_rgb  # noqa: F401

_poller = None

def poll():
    global _poller
    return _poller()

class DTDisplay():
    def __new__(cls, *args, **kwargs):
        global _poller
        try:
            from . import sdldisplay
            instance = sdldisplay.SDLDisplay(*args, **kwargs)
            _poller = sdldisplay.poll
        except Exception as e:
            import sys
            if sys.implementation.name == "micropython":
                raise Exception(e)
            else:
                from . import pgdisplay
                instance = pgdisplay.PGDisplay(*args, **kwargs)
                _poller = pgdisplay.poll
        return instance
