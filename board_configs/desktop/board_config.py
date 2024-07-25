"""
Combination board configuration for desktop platforms.

Tested with CPython on Linux, Windows and ChromeOS.
Tested with MicroPython on Linux.
Should work on MacOS, but not tested.
"""
from mpdisplay.dtdisplay import DTDisplay  #, Events, Devices
import sys


display_drv = DTDisplay(
    width=320,
    height=480,
    rotation=0,
    color_depth=16,
    title=f"{sys.implementation.name} on {sys.platform}",
    scale=1.0,
)

events_dev = display_drv.broker.create_device(
    # type=Devices.QUEUE,
    read=display_drv.read,
    # data=Events.filter,
)
