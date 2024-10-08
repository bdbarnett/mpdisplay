"""
Board configuration for Jupyter Notebook.

"""
from jndisplay import JNDisplay
from timer import get_timer


display_drv = JNDisplay(480, 320)
tim = get_timer(display_drv.show)
