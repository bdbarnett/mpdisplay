"""
Board configuration for Jupyter Notebook.
"""

from displaysys.jndisplay import JNDisplay
from eventsys import device


width = 320
height = 480

broker = device.Broker()

display_drv = JNDisplay(width, height)

display_drv.fill(0)
