"""
Combination board configuration for desktop, pyscript and jupyter notebook platforms.
"""

from displaysys.sdldisplay import SDLDisplay as DTDisplay, poll
from eventsys import device
import sys

width = 320
height = 480
rotation = 0
scale = 2.0

display_drv = DTDisplay(
    width=width,
    height=height,
    rotation=rotation,
    title=f"{sys.implementation.name} on {sys.platform}",
    scale=scale,
)

broker = device.Broker()

events_dev = broker.create_device(
    type=device.Types.QUEUE,
    read=poll,
    data=display_drv,
    # data2=Events.filter,
)

display_drv.fill(0)
