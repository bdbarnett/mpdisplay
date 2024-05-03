"""
Combination board configuration for desktop platforms.

Tested with CPython on Linux, Windows and ChromeOS.
Tested with MicroPython on Linux.
Should work on MacOS, but not tested.
"""
import mpdisplay
import sys

display_drv = mpdisplay.SDL2Display(
    width=320,
    height=480,
    title=f"{sys.implementation.name} on {sys.platform}",
    window_flags=mpdisplay.SDL_WINDOW_SHOWN,
    color_depth=16,
    x=mpdisplay.SDL_WINDOWPOS_CENTERED,
    y=mpdisplay.SDL_WINDOWPOS_CENTERED,
    render_flags=mpdisplay.SDL_RENDERER_ACCELERATED,
    scale=1.5,
)

display_drv.quit_func = sys.exit

events_drv = mpdisplay.SDL2Events()

events_dev = display_drv.create_device(
    type=mpdisplay.Devices.EVENTS,
    read=events_drv.read,
    data=mpdisplay.Events.types
    )
