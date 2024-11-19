"""
Combination board configuration for desktop platforms.

Tested with CPython on Linux, Windows and ChromeOS.
Tested with MicroPython on Linux.
Should work on MacOS, but not tested.
"""

from dtdisplay import DTDisplay, poll
import eventsys.device as device
import sys


display_drv = DTDisplay(
    width=320,
    height=480,
    rotation=0,
    color_depth=16,
    title=f"{sys.implementation.name} on {sys.platform}",
    scale=1.0,
)

broker = device.Broker()

events_dev = broker.create_device(
    type=device.Types.QUEUE,
    read=poll,
    data=display_drv,
    # data2=Events.filter,
)
