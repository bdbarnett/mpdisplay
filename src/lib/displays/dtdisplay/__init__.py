"""
PyDevices dtdisplay
"""

from basedisplay import DisplayDriver, Area, color_rgb  # noqa: F401

_poller = None


def poll():
    global _poller
    return _poller()


class DTDisplay:
    def __new__(cls, *args, **kwargs):
        global _poller
        try:
            from . import pgdisplay

            instance = pgdisplay.PGDisplay(*args, **kwargs)
            _poller = pgdisplay.poll
        except Exception:
            from . import sdldisplay

            instance = sdldisplay.SDLDisplay(*args, **kwargs)
            _poller = sdldisplay.poll
        return instance
