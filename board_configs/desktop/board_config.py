"""
Combination board configuration for desktop platforms.

Tested with CPython on Linux, Windows and ChromeOS.
Tested with MicroPython on Linux.
Should work on MacOS, but not tested.
"""
import mpdisplay
import sys


# This is an example of how to access pygame or SDL2 constants.  You can delete this.
if hasattr(mpdisplay, "pg"):
    BORDERLESS = mpdisplay.pg.NOFRAME
elif hasattr(mpdisplay, "sdl2"):
    BORDERLESS = mpdisplay.sdl2.SDL_WINDOW_BORDERLESS
else:
    raise ImportError("No supported display backend found.\nThis board_config.py is for desktop platforms only.\nPlease install Pygame or SDL2.\n")

display_drv = mpdisplay.DesktopDisplay(
    width=320,
    height=480,
    rotation=0,
    color_depth=16,
    title=f"{sys.implementation.name} on {sys.platform}",
#     window_flags=BORDERLESS,
    scale=1.5,
)

events_drv = mpdisplay.DesktopEvents()

events_dev = display_drv.create_device(
    type=mpdisplay.Devices.EVENT,
    read=events_drv.read,
    data=mpdisplay.Events.types
    )
