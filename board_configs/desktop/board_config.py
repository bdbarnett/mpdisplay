"""
Combination board configuration for desktop platforms.

Tested with CPython on Linux, Windows and ChromeOS.
Tested with MicroPython on Linux.
Should work on MacOS, but not tested.
"""
from dtdisplay import DTDisplay, poll # type: ignore
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

broker = Broker()

events_dev = broker.create_device(
    type=Devices.QUEUE,
    read=poll,
    data=display_drv,
    # data2=Events.filter,
)
