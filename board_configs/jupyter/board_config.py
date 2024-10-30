"""
Board configuration for Jupyter Notebook.

"""
from jndisplay import JNDisplay
from pydevices.devices import Broker


broker = Broker()

display_drv = JNDisplay(480, 320)
