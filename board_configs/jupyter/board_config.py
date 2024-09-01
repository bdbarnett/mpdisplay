"""
Board configuration for Jupyter Notebook.

"""
from jndisplay import JNDisplay
from timer import refresh_timer


display_drv = JNDisplay(480, 320)
tim = refresh_timer(display_drv.show)
