"""
Board configuration for Jupyter Notebook.

"""

from jndisplay import JNDisplay
import eventsys.device as device


broker = device.Broker()

display_drv = JNDisplay(480, 320)
