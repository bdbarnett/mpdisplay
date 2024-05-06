"""
Combination board configuration for desktop platforms.

Tested with CPython on Linux, Windows and ChromeOS.
Tested with MicroPython on Linux.
Should work on MacOS, but not tested.
"""
from mpdisplay import DesktopDisplay, DesktopEvents, Devices, Events
import sys

display_drv = DesktopDisplay(
    width=320,
    height=480,
    rotation=0,
    color_depth=16,
    title=f"{sys.implementation.name} on {sys.platform}",
    scale=1,
)

events_drv = DesktopEvents()

events_dev = display_drv.create_device(
    type=Devices.EVENT,
    read=events_drv.read,
    data=Events.types
    )
