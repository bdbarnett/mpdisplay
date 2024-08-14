"""
Combination board configuration for desktop platforms.

Tested with CPython on Linux, Windows and ChromeOS.
Tested with MicroPython on Linux.
Should work on MacOS, but not tested.
"""
from displays.dtdisplay import DTDisplay, poll # type: ignore
from eventsys.devices import Devices, Broker # type: ignore
import sys


display_drv = DTDisplay(
    width=320,
    height=480,
    rotation=0,
    color_depth=16,
    title=f"{sys.implementation.name} on {sys.platform}",
    scale=1.0,
)

display_drv.broker = Broker()

events_dev = display_drv.broker.create_device(
    type=Devices.QUEUE,
    read=poll,
    # data=Events.filter,
)
